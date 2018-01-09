from django.conf.urls import include, url
from django.contrib import admin
from markdownx import urls as markdownx

urlpatterns = [
    url(r'^', include('app.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^markdownx/', include(markdownx)),
    url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
]

