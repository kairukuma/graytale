from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.room,name='index'),
    url(r'^create/$',views.create,name='create'),
    url(r'^g/(?P<room_name>[^/]+)/$',views.room,name='room'),
    url(r'^g/(?P<room_name>[^/]+)/(?P<post_id>[^/]+)/$',views.post_view,name='post'),
    url(r'^g/(?P<room_name>[^/]+)/(?P<post_id>[^/]+)/edit/$',views.edit_post_view),
    url(r'^g/(?P<room_name>[^/]+)/(?P<post_id>[^/]+)/delete/$',views.delete_post_view),
    url(r'^user/(?P<user_name>[^/]+)/$',views.user,name='user_page'),
    url(r'^user/(?P<user_name>[^/]+)/(?P<msg_page>[^/]+)/(?P<post_page>[^/]+)$',views.user,name='user_page'),
    url(r'^notifications/$', views.notifications),
    url(r'^sendpush/', views.sendpush),
]

account_urlpatterns = [
    url(r'^register/', views.Register.as_view(), name='register'),
]