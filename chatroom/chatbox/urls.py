from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.room,name='index'),
    url(r'^create/',views.create,name='create'),
    url(r'^g/(?P<room_name>[^/]+)/$',views.room,name='room'),
    url(r'^g/(?P<room_name>[^/]+)/(?P<post_id>[^/]+)$',views.post_view,name='post'),
]

account_urlpatterns = [
    url(r'^register/', views.Register.as_view(), name='register'),
]