import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mtbhouse.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
