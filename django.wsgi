# -*- coding: utf-8 -*-
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "/")))

os.environ['DJANGO_SETTINGS_MODULE'] = 'djbook.settings'
os.environ['PYTHON_EGG_CACHE'] = '/home/tim/.python-eggs'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


