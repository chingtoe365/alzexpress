"""
WSGI config for ADDB project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os, sys

# add the alzexpress project path into the sys.path
sys.path.append('/home/alzexpress/alzexpress')

# add the virtualenv site-packages path to the sys.path
sys.path.append('/home/alzexpress/addbenv/lib/python2.7/site-packages')

# pointing to the project settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ADDB.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
