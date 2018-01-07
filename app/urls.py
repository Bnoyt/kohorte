from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^whatsup/$', views.whatsup, name='whatsup'),
    url(r'^login/$',views.page_login, name='login'),
    url(r'^register/$',views.page_register, name='register'),
    url(r'^noeud/(?P<noeud_id>[0-9]+)/$', views.noeud, name='noeud'),
    url(r'^parametres/$',views.parametres,name='parametres'),
    url(r'^ajouter_post/$',views.ajouter_post,name='ajouter_post'),
    url(r'^ajouter_commentaire/$',views.ajouter_commentaire,name='ajouter_commentaire'),
    url(r'^ajouter_reponse/$',views.ajouter_reponse,name='ajouter_reponse'),
    url(r'^sauvegarder_citation/$',views.sauvegarder_citation,name='sauvegarder_citation'),
    url(r'^faq/$',views.faq,name='faq'),
]