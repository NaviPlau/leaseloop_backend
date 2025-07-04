from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lease_auth'

    def ready(self):
        import lease_auth.signals  
