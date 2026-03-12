from .static_labels import STATIC_GESTURES
from .dynamic_labels import DYNAMIC_GESTURES


STATIC_LABEL_MAP = {
    name: i for i, name in enumerate(STATIC_GESTURES)
}

STATIC_ID_MAP = {
    i: name for i, name in enumerate(STATIC_GESTURES)
}


DYNAMIC_LABEL_MAP = {
    name: i for i, name in enumerate(DYNAMIC_GESTURES)
}

DYNAMIC_ID_MAP = {
    i: name for i, name in enumerate(DYNAMIC_GESTURES)
}