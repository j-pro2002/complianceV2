from django.urls import path
from . import views

urlpatterns = [
    # URL pour la connexion
    path('', views.utilisateur_login, name='login'),

    # URL pour la déconnexion
    path('logout/', views.utilisateur_logout, name='logout'),

    # URL pour la page de profil de l'utilisateur
    path('profile/', views.user_profile, name='profile'),

    # URL pour créer un nouvel utilisateur (administration)
    path('create/', views.utilisateur_create, name='create_utilisateur'),

    # URL pour mettre à jour un utilisateur existant (administration)
    path('update/<int:pk>/', views.utilisateur_update, name='update_utilisateur'),

    # URL pour changer le mot de passe de l'utilisateur
    path('change_password/', views.change_password, name='change_password'),

    # URL pour vérifier l'OTP
    path('otp_verify/', views.verify_otp, name='otp_verify'),
]
