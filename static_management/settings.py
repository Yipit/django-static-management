import logging

from django.conf import settings

STATIC_MANAGEMENT_COMPRESS_CMD = getattr(settings, 'STATIC_MANAGEMENT_COMPRESS_CMD', '')
STATIC_MANAGEMENT_CSS_LINK = getattr(settings, 'STATIC_MANAGEMENT_CSS_LINK', '')
STATIC_MANAGEMENT_SCRIPT_SRC = getattr(settings, 'STATIC_MANAGEMENT_SCRIPT_SRC', '<script type="text/javascript" src="%s"></script>\n')
STATIC_MANAGEMENT_VERSIONER = getattr(settings, 'STATIC_MANAGEMENT_VERSIONER','static_management.versioners.SHA1Sum')
STATIC_MANAGEMENT = getattr(settings, 'STATIC_MANAGEMENT',{})
STATIC_MANAGEMENT_USE_VERSIONS = getattr(settings, 'STATIC_MANAGEMENT_USE_VERSIONS',True)
STATIC_MANAGEMENT_SYNC_COMMAND = getattr(settings, 'STATIC_MANAGEMENT_SYNC_COMMAND', '')

STATIC_MANAGEMENT_LOGGER = getattr(settings, 'STATIC_MANAGEMENT_LOGGER', '')
STATIC_MANAGEMENT_LOGGING_LEVEL = getattr(settings, 'STATIC_MANAGEMENT_LOGGING_LEVEL', '')

if not STATIC_MANAGEMENT_LOGGER:
    logger = logging.getLogger('static_management')
    if len(logger.handlers) < 1:
        logger.addHandler(loggingStreamHandler())
    if STATIC_MANAGEMENT_LOGGING_LEVEL:
        logger.setLevel(STATIC_MANAGEMENT_LOGGING_LEVEL)
    STATIC_MANAGEMENT_LOGGER = 'static_management'

MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
DEBUG = getattr(settings, 'DEBUG')