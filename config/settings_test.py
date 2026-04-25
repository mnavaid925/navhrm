from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

DEBUG = False
SECRET_KEY = 'test-only-secret-key-not-for-production'  # noqa: S105

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

import tempfile
MEDIA_ROOT = tempfile.mkdtemp(prefix='navhrm-test-media-')

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
