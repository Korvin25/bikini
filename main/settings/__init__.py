from .base import *

try:
    from .local import *
except ImportError:
    pass

try:
    TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
except NameError:
    pass
