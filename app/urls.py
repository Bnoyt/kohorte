from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$',views.page_login, name='login'),
    url(r'^register/$',views.page_register, name='register'),
    url(r'^noeud/(?P<noeud_id>[0-9]+)/$', views.noeud, name='noeud'),
    url(r'^parametres/$',views.parametres,name='parametres'),
    url(r'^ajouter_post/$',views.ajouter_post,name='ajouter_post')
]