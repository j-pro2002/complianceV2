from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('agent', 'Agent'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='agent', verbose_name="Rôle")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Numéro de téléphone")  # Nouveau champ
    fullname = models.CharField(max_length=255, default='Orange')
    mail_user = models.CharField(max_length=255, default='mail@gmail.com')
 
    def update_fullname(self, new_fullname):
        if self.fullname == 'Orange':  # Ne met à jour que si le fullname est encore 'Orange'
            self.fullname = new_fullname
            self.save()
    def update_email(self, new_email):
        if self.mail_user == 'mail@gmail.com':
            self.mail_user  = new_email
            self.save()
    
    def update_phone(self, new_phone):
        if self.phone == '':
            self.phone  = new_phone
            self.save()

    def __str__(self):
        return self.username
