from django.apps import AppConfig


class LabSessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lab_sessions'

    def ready(self):
        import apps.lab_sessions.signals
