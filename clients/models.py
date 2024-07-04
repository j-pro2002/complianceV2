from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('closed', 'Clos'),
    )
    CONTACT_METHOD_CHOICES = (
        ('email', 'Email'),
        ('phone', 'Téléphone'),
    )
    SEX_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    
    # Identité de l'agent
    agent_identity = models.CharField(max_length=100, verbose_name="Identité de l'agent", default="Inconnu", blank=True, null=True)
    
    # Identité du plaignant
    complainant_name = models.CharField(max_length=100, verbose_name="Nom du plaignant", default="Anonyme")
    complainant_address = models.TextField(verbose_name="Adresse du plaignant", default="Adresse non fournie")
    complainant_email = models.EmailField(verbose_name="Email du plaignant", default="email@exemple.com")
    complainant_phone = models.CharField(max_length=15, verbose_name="Téléphone du plaignant", default="0000000000")
    complainant_sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Sexe du plaignant", default='M')
    
    # Sujet et Description
    subject = models.CharField(max_length=200, verbose_name="Sujet", default="Sujet non défini")
    description = models.TextField(verbose_name="Description/Detail", default="Pas de description fournie")
    
    # Statut
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Dates
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    # Fichiers
    report_file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name='Procès-verbal')
    proof_file = models.FileField(upload_to='proofs/', blank=True, null=True, verbose_name='Fichier de preuve')
    
    # Moyen de contact
    preferred_contact_method = models.CharField(max_length=10, choices=CONTACT_METHOD_CHOICES, verbose_name="Moyen de contact", default='email')

    # Slug
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        base_slug = slugify(self.subject)
        slug = base_slug
        counter = 1
        while Complaint.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
    def get_absolute_url(self):
        return reverse('complaint_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return f"Plainte de {self.complainant_name} - {self.subject}"
