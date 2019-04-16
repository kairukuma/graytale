from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message

@receiver(post_save,sender=Message)
def receiver(sender, **kwargs):
    m = kwargs['instance']
    print("Serverside received message %d (user:%s, topic:%s, text:%s)" % (m.post_id,m.username,m.room_name,m.message_text))