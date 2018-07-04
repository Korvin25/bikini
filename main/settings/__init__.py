from .base import *

try:
    from .local import *
except ImportError:
    pass

try:
    TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
except NameError:
    pass

try:
    REQUEST_BASE_URL = 'https://{}'.format(DEFAULT_SITENAME)
except NameError:
    pass
