from django.contrib.auth import logout

def effacer_session_si_connecte(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)  # Déconnexion de l'utilisateur si déjà connecté
        return view_func(request, *args, **kwargs)
    return wrapper