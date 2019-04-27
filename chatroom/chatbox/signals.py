from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save,sender=Message)
def receiver(sender, **kwargs):
    m = kwargs['instance']
    print("Serverside received message %d (user:%s, topic:%s, text:%s)" % (int(m.post_id),m.username,m.room_name,m.message_text))

def notification_created(sender, **kwargs):
    n = kwargs['instance']
    #print("Create notification {} for users {}".format(n.name,n.users.all()))

post_save.connect(notification_created, sender=Notification)