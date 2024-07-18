from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Utilisateur
import requests
import xml.etree.ElementTree as ET
from django.utils import timezone
from .models import Utilisateur
from .decorators import *
# Fonction pour envoyer un OTP via l'Api orange

def send_otp_via_api(destination):
    url = 'http://10.25.3.81:5002/api/generate'
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }
    
    if '@orange.com' in destination:
        payload = {
            "reference": destination,
            "origin": "compliance",
            "otpOveroutTime": 300000,
            "customMessage": "Dear customer, {{ otpCode }} is your OTP code. Go back to our platform and enter it to log in.",
            "senderName": "orange@orange.com",
            "ignoreOrangeNumbers": False
        }
    else:
        payload = {
            "reference": destination,
            "origin": "compliance",
            "otpOveroutTime": 300000,
            "customMessage": "Dear customer, {{ otpCode }} is your OTP code. Go back to our platform and enter it to log in.",
            "senderName": "Orange Compliances",
            "ignoreOrangeNumbers": False
        }

    
    try:
        print(f" send OTP  payload {payload}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending OTP via API: {str(e)}")
        raise

# Fonction pour vérifier l'OTP via l'Api orange

def check_otp_via_api(reference, input_otp):
    url = 'http://10.25.3.81:5002/api/check'
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }
    payload = {
        "reference": reference,
        "origin": "compliance",
        "receivedOtp": input_otp,
        "ignoreOrangeNumbers": False
    }
    
    try:
        print(f" check OTP  payload {payload}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error checking OTP via API: {str(e)}")
        raise
 
# Fonction pour authentifier l'utilisateur via LDAP et récupérer les informations

def authenticate_via_ldap(username, password):
    url = 'http://10.25.2.25:8080/ldap/'  
    headers = {'Content-Type': 'application/xml'}
    payload = f"""
    <COMMANDE>
        <TYPE>AUTH_SVC</TYPE>
        <APPLINAME>Test</APPLINAME>
        <CUID>{username}</CUID>
        <PASSWORD>{password}</PASSWORD>
        <DATE>{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}</DATE>
    </COMMANDE>
    """
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        req_status = root.find('REQSTATUS').text
        if req_status == 'SUCCESS':
            phone_number = root.find('PHONENUMBER').text
            email = root.find('EMAIL').text
            full_name = root.find('FULLNAME').text
            
            if phone_number :
                phone_number_part = phone_number.split(' ')
                cleaned_phone_number = '+243 ' + ''.join(phone_number_part[1:])
                phone_number = cleaned_phone_number

            try:
                user = Utilisateur.objects.get(username=username)
                user.update_fullname(full_name)
                user.update_email(email)
                user.update_phone(phone_number) 

                print (f"{phone_number} ----  {email}")
                return phone_number, email
            except Utilisateur.DoesNotExist:
                print(f"Utilisateur {username} non trouvé.")
                return None, None
        else:
            return None, None
    except requests.RequestException as e:
        print(f"Error authenticating via LDAP: {str(e)}")
        return None, None

# Vue pour la connexion de l'utilisateur

def utilisateur_login(request):

    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        phone_number, email = authenticate_via_ldap(username, password)
        print(f'{phone_number} --- {email}')

        if phone_number is None and email is None:
            messages.error(request, 'Vous n\'êtes pas autorisé à accéder à ce service.')
            return redirect('login')


        user = authenticate(request, username=username, password='jjjjjjjjjj')

        if user is not None:
            if user.is_active:
                preferred_contact = phone_number if phone_number else email
                if not preferred_contact:
                    messages.error(request, 'Aucune adresse email ou numéro de téléphone n\'est disponible pour cet utilisateur.')
                    return redirect('login')

                try:
                    # Envoyer l'OTP via l'API externe
                    response = send_otp_via_api(preferred_contact)
                    otp = response.get('otp')

                    request.session['otp'] = otp
                    request.session['reference'] = preferred_contact
                    request.session['user_id'] = user.id
                    messages.info(request, f'Un code OTP a été envoyé à votre {"numéro de téléphone" if phone_number else "email"}. Veuillez le saisir pour continuer.')
                    return redirect('otp_verify')

                except requests.RequestException as e:
                    messages.error(request, f"Erreur lors de l'envoi de l'OTP via l'API : {str(e)}")
                    return redirect('login')

            else:
                messages.error(request, 'Votre compte est inactif. Veuillez contacter l\'administrateur.')
        else:
            messages.error(request, 'Vous n\'êtes pas autorisé à accéder à ce service.')

    return render(request, 'login.html')

# Vue pour vérifier l'OTP

def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        reference = request.session.get('reference')
        user_id = request.session.get('user_id')

        try:
            # Vérifier l'OTP via l'API externe
            response = check_otp_via_api(reference, input_otp)
            if response['code'] == 200 and response['diagnosticResult']:
                user = Utilisateur.objects.get(id=user_id)
                login(request, user)

                del request.session['otp']
                del request.session['reference']
                del request.session['user_id']

                messages.success(request, 'OTP vérifié avec succès. Vous êtes maintenant connecté.')

                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return redirect('complaint_list')

            else:
                messages.error(request, 'Code OTP incorrect. Veuillez réessayer.')

        except Utilisateur.DoesNotExist:
            messages.error(request, 'Utilisateur introuvable. Veuillez réessayer.')

        except requests.RequestException as e:
            messages.error(request, f"Erreur lors de la vérification de l'OTP via l'API : {str(e)}")

    return render(request, 'two_step.html')

# Vue pour déconnecter l'utilisateur

def utilisateur_logout(request):
    logout(request)
    messages.success(request, 'Vous êtes maintenant déconnecté.')
    return redirect('login')

# Vue pour créer un nouvel utilisateur (réservé aux administrateurs)
@staff_member_required
def utilisateur_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        
        if Utilisateur.objects.filter(username=username).exists() or Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.')
        else:
            user = Utilisateur.objects.create_user(username=username, email=email, password='orange')
            user.is_staff = True if role == 'admin' else False
            user.save()
            messages.success(request, f'Utilisateur {user.username} créé avec succès.')
            return redirect('home')
    return render(request, 'utilisateur_create.html')

# Vue pour mettre à jour un utilisateur existant (réservé aux administrateurs)
@staff_member_required
def utilisateur_update(request, pk):
    user = get_object_or_404(Utilisateur, pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        
        if (username != user.username and Utilisateur.objects.filter(username=username).exists()) or \
           (email != user.email and Utilisateur.objects.filter(email=email).exists()):
            messages.error(request, 'Un utilisateur avec ce nom d\'utilisateur ou cet email existe déjà.')
        else:
            user.username = username
            user.email = email
            user.is_staff = True if role == 'admin' else False
            user.save()
            messages.success(request, f'Informations de l\'utilisateur {user.username} mises à jour avec succès.')
            return redirect('home')
    
    return render(request, 'utilisateur_update.html', {'user': user})

# Vue pour permettre à l'utilisateur de changer son mot de passe
@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        else:
            user = request.user
            if not user.check_password(old_password):
                messages.error(request, 'Votre ancien mot de passe est incorrect.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Votre mot de passe a été changé avec succès.')
                return redirect('home')
    
    return render(request, 'change_password.html')

@login_required
def user_profile(request):
    """
    Affiche la page de profil de l'utilisateur.
    """
    user = request.user
    context = {'user': user}
    return render(request, 'userpage.html', context)