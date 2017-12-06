from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('app.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^noeud/(?P<noeud_id>[0-9]+)/$', views.noeud, name='noeud')
]