# complaints/decorators.py

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse

def super_admin_only(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.is_superuser:
            if request.path.startswith('/admin/'):
                return view_func(request, *args, **kwargs)
            else:
                logout(request)
                return redirect(reverse('login'))  # Redirige vers l'URL de connexion spécifiée
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view_func
