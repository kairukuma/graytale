from django.apps import AppConfig


class ChatboxConfig(AppConfig):
    name = 'chatbox'

    def ready(self):
        import chatbox.signals
