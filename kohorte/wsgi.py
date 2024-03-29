"""
WSGI config for kohorte project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kohorte.settings")

import django
django.setup()


import kohorte.startup as startup
startup.run()

application = get_wsgi_application()
