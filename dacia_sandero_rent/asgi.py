

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dacia_sandero_rent.settings')

application = get_asgi_application()
