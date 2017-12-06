from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$',views.page_login, name='login'),
    url(r'^register/$',views.page_register, name='register'),
    
    
]