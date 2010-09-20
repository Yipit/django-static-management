from django.conf import settings

STATIC_MANAGEMENT_COMPRESS_CMD = getattr(settings, 'STATIC_MANAGEMENT_CSS_LINK', '')
STATIC_MANAGEMENT_CSS_LINK = getattr(settings, 'STATIC_MANAGEMENT_CSS_LINK', '')
STATIC_MANAGEMENT_SCRIPT_SRC = getattr(settings, 'STATIC_MANAGEMENT_SCRIPT_SRC', '<script type="text/javascript" src="%s"></script>\n')
STATIC_MANAGEMENT_CACHEBUST = getattr(settings, 'STATIC_MANAGEMENT_CACHEBUST', '')
STATIC_MANAGEMENT_CSS_ASSET_PATTERN = getattr(settings, 'STATIC_MANAGEMENT_CSS_ASSET_PATTERN', '(?P<url>url(\([\'"]?(?P<filename>[^)]+\.[a-z]{3,4})(?P<fragment>#\w+)?[\'"]?\)))')
STATIC_MANAGEMENT_ASSET_PATHS = getattr(settings, 'STATIC_MANAGEMENT_ASSET_PATHS', [])
STATIC_MANAGEMENT_HOSTNAMES = getattr(settings, 'STATIC_MANAGEMENT_HOSTNAMES', [])
STATIC_MANAGEMENT_VERSIONER = getattr(settings, 'STATIC_MANAGEMENT_VERSIONER','static_management.versioners.SHA1Sum')