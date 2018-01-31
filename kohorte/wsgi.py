"""
WSGI config for kohorte project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import kohorte.startup as startup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kohorte.settings")

#startup.run()

application = get_wsgi_application()
