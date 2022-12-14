from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
    url(r'^ws/(?P<room_name>[^/]+)/(?P<post_id>[^/]+)/$', consumers.ChatConsumer),
    # url(r'^nws/notifications/$', consumers.NotificationConsumer),
]