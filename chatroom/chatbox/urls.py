from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$',views.index,name='index'),
    url(r'^$',views.room,name='index'),
    url(r'^(?P<room_name>[^/]+)/$',views.room,name='room'),
    # url('^graytale/', django.views.defaults.page_not_found),
]