from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project_id>[0-9]+)/$', views.whatsup, name='whatsup'),
    url(r'^login/$',views.page_login, name='login'),
    url(r'^register/$',views.page_register, name='register'),
    url(r'^noeud/(?P<noeud_id>[0-9]+)/$', views.noeud, name='noeud'),
    url(r'^parametres/$',views.parametres,name='parametres'),
    url(r'^ajouter_post/$',views.ajouter_post,name='ajouter_post'),
    url(r'^ajouter_commentaire/$',views.ajouter_commentaire,name='ajouter_commentaire'),
    url(r'^ajouter_reponse/$',views.ajouter_reponse,name='ajouter_reponse'),
    url(r'^sauvegarder_citation/$',views.sauvegarder_citation,name='sauvegarder_citation'),
    url(r'^faq/$',views.faq,name='faq'),
    url(r'^profil/$',views.profil,name='profil'),
    url(r'^hashtags/(?P<project_id>[0-9]+)/(?P<hashtag>[0-9a-zA-Z]+)/$',views.hashtags,name='hashtags'),
    url(r'^suivi_noeud/$',views.suivi_noeud,name='suivi_noeud'),
    url(r'^vote/$',views.vote,name='vote'),
]
