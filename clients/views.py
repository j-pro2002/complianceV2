from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .models import Complaint
from user.models import Utilisateur
from django.core.exceptions import ValidationError
from .decorators import super_admin_only

@super_admin_only
def home_complaint(request):
    """
    Vue pour la page d'accueil des plaintes réservée aux super administrateurs.

    :param request: Objet HttpRequest
    :return: Objet HttpResponse
    """
    return render(request, 'complients/index.html')

@login_required
@super_admin_only
def complaint_list(request):
    """
    Vue pour lister toutes les plaintes avec des statistiques.

    :param request: Objet HttpRequest
    :return: Objet HttpResponse
    """
    try:
        complaints = Complaint.objects.all()
        complaints_order = Complaint.objects.order_by('-date_created')

        
        
        context = {
            'complaints': complaints_order,
            'total_complaints': complaints.count(),
            'closed_complaints': complaints.filter(status='closed').count(),
            'pending_complaints': complaints.filter(status='pending').count(),
        }
        
        return render(request, 'complients/complient.html', context)

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la récupération des plaintes : {str(e)}")
        return redirect('home_complaint')

@super_admin_only
def submit_complaint(request):
    """
    Vue pour soumettre une nouvelle plainte.

    :param request: Objet HttpRequest
    :return: Objet HttpResponse
    """
    if request.method == 'POST':
        try:
            case_type = request.POST.get('q_1')
            agent_identity = request.POST.get('q_2')
            name = request.POST.get('full_name')
            address = request.POST.get('address')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            sex = request.POST.get('gender')
            description = request.POST.get('description')
            preferred_contact_method = request.POST.get('preferred_contact_method')

            proof_file = request.FILES.get('proof_file')

            complaint = Complaint.objects.create(
                subject=case_type,
                agent_identity=agent_identity,
                complainant_name=name,
                complainant_address=address,
                complainant_email=email,
                complainant_phone=phone,
                complainant_sex=sex,
                description=description,
                proof_file=proof_file,
                preferred_contact_method=preferred_contact_method,
            )

            users = Utilisateur.objects.all()
            for user in users:
                try:
                    context = {
                        'complaint': complaint,
                        'username': user.username,
                        'request': request,
                    }
                    subject = 'Nouvelle plainte déposée'
                    html_message = render_to_string('complients/new_complaint.html', context)
                    plain_message = strip_tags(html_message)
                    from_email = 'no-reply@orange-rdc.com'
                    to_email = user.email

                    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

                except Exception as e:
                    print(f"Erreur lors de l'envoi de l'email à {user.username}: {str(e)}")

            messages.success(request, 'La plainte a été soumise avec succès.')
            return redirect('success')

        except ValidationError as e:
            messages.error(request, f"Erreur de validation lors de la soumission de la plainte : {str(e)}")
            return redirect('submit_complaint')

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de la soumission de la plainte : {str(e)}")
            return redirect('submit_complaint')

    return render(request, 'complients/form.html')

@login_required
@super_admin_only
def complaint_detail(request, slug):
    """
    Vue pour afficher les détails d'une plainte spécifique.

    :param request: Objet HttpRequest
    :param slug: Slug de la plainte
    :return: Objet HttpResponse
    """
    try:
        complaint = get_object_or_404(Complaint, slug=slug)
        return render(request, 'complients/complient-detail.html', {'complaint': complaint})

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de l'affichage des détails de la plainte : {str(e)}")
        return redirect('home_complaint')

@login_required
@super_admin_only
def update_complaint(request, slug):
    """
    Vue pour mettre à jour une plainte avec un procès-verbal.

    :param request: Objet HttpRequest
    :param slug: Slug de la plainte
    :return: Objet HttpResponse
    """
    try:
        complaint = get_object_or_404(Complaint, slug=slug)
        
        if request.method == 'POST':
            report_file = request.FILES.get('report_file')
            if report_file:
                complaint.report_file = report_file
                complaint.status = 'closed'
                complaint.save()

                users = Utilisateur.objects.all()
                email_addresses = [user.email for user in users]

                subject = "Plainte clôturée avec un procès-verbal"
                context = {
                    'complaint': complaint,
                    'username': request.user.username,
                }
                html_message = render_to_string('complients/complaint_closed.html', context)
                plain_message = strip_tags(html_message)

                send_mail(
                    subject,
                    plain_message,
                    'Orange RDC <no-reply@orange-rdc.com>',
                    email_addresses,
                    html_message=html_message,
                    fail_silently=False,
                )

                messages.success(request, 'Le procès-verbal a été ajouté avec succès.')
                return redirect('complaint_detail', slug=slug)

            else:
                messages.error(request, 'Veuillez choisir un fichier pour mettre à jour le procès-verbal.')

        return render(request, 'complients/complient-detail.html', {'complaint': complaint})

    except ValidationError as e:
        messages.error(request, f"Erreur de validation lors de la mise à jour de la plainte : {str(e)}")
        return redirect('complaint_detail', slug=slug)

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la mise à jour de la plainte : {str(e)}")
        return redirect('complaint_detail', slug=slug)

@login_required
@super_admin_only
def delete_complaint(request, slug):
    """
    Vue pour supprimer une plainte.

    :param request: Objet HttpRequest
    :param slug: Slug de la plainte
    :return: Objet HttpResponse
    """
    try:
        complaint = get_object_or_404(Complaint, slug=slug)
        
        if request.method == 'POST':
            complaint_details = {
                'subject': complaint.subject,
                'description': complaint.description,
            }
            complaint.delete()
            messages.success(request, 'La plainte a été supprimée avec succès.')

            users = Utilisateur.objects.all()

            for user in users:
                try:
                    context = {
                        'complaint_details': complaint_details,
                        'username': user.username,
                    }
                    subject = "Notification de suppression de plainte"
                    html_message = render_to_string('complients/complaint_deleted.html', context)
                    plain_message = strip_tags(html_message)
                    from_email = 'no-reply@orange-rdc.com'
                    to_email = user.email

                    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

                except Exception as email_error:
                    print(f"Erreur lors de l'envoi de l'email à {user.username}: {str(email_error)}")

            return redirect('complaint_list')
        
        return render(request, 'complients/complient.html', {'complaint': complaint})

    except Exception as e:
        messages.error(request, f"Une erreur s'est produite lors de la suppression de la plainte : {str(e)}")
        return redirect('complaint_list')

@super_admin_only
def success_view(request):
    """
    Vue pour afficher la page de succès après soumission d'une plainte.

    :param request: Objet HttpRequest
    :return: Objet HttpResponse
    """
    return render(request, 'complients/success.html')
