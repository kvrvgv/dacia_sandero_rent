

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacia_sandero_rent.settings')

application = get_wsgi_application()
