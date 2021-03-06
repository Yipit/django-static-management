import os

from django import template
register = template.Library()

from static_management import settings
from static_management.models import FileVersion

SUPPORTED_FILE_TYPES = ['css', 'js']
FILE_VERSIONS = {}

for inheritance_key in SUPPORTED_FILE_TYPES:
    FILE_VERSIONS[inheritance_key] = {}
    try:
        file_keys = settings.STATIC_MANAGEMENT[inheritance_key]
    except KeyError:
        continue
    for file_key in file_keys:
        if settings.STATIC_MANAGEMENT_USE_VERSIONS:
            try:
                filename = FileVersion.objects.get(file_key=file_key).filename
                FILE_VERSIONS[inheritance_key][file_key] = filename
                continue
            except FileVersion.DoesNotExist:
                pass

        FILE_VERSIONS[inheritance_key][file_key] = file_key


@register.simple_tag(takes_context=True)
def static_combo_css(context, file_name, media=None):
    """combines files in settings
    {% static_combo_css "css/main.css" %}"""
    # override the default if an override exists
    if settings.STATIC_MANAGEMENT_CSS_LINK:
        link_format = settings.STATIC_MANAGEMENT_CSS_LINK
    else:
        if media:
            link_format = '<link rel="stylesheet" type="text/css" href="%%s" media="%s">\n' % media
        else:
            link_format = '<link rel="stylesheet" type="text/css" href="%s">\n'
    gzipped = ('gzip' in context['request'].META.get('HTTP_ACCEPT_ENCODING', " ") and not settings.DEBUG)
    output = _group_file_names_and_output(file_name, link_format, 'css', gzipped, media_url=settings.CSS_MEDIA_URL)
    return output


@register.simple_tag(takes_context=True)
def static_combo_js(context, file_name):
    """combines files in settings
    {% static_combo_js "js/main.js" %}"""
    script_format = settings.STATIC_MANAGEMENT_SCRIPT_SRC
    gzipped = ('gzip' in context['request'].META.get('HTTP_ACCEPT_ENCODING', " ") and not settings.DEBUG)
    output = _group_file_names_and_output(file_name, script_format, 'js', gzipped, media_url=settings.JS_MEDIA_URL)
    return output


def _group_file_names_and_output(parent_name, output_format, inheritance_key, gzipped=False, media_url=settings.MEDIA_URL):
    """helper function to do most of the heavy lifting of the above template tags"""
    try:
        file_names = settings.STATIC_MANAGEMENT[inheritance_key][parent_name]
    except AttributeError:
        raise template.TemplateSyntaxError, "%s not in static combo settings" % parent_name
    output = ''
    if not settings.SERVE_COMPRESSED:
        # we need to echo out each one
        for file_name in file_names:
            file_path = os.path.join(settings.STATIC_MANAGEMENT_ROOT, file_name)
            if file_name in settings.STATIC_MANAGEMENT[inheritance_key]:
                output += _group_file_names_and_output(file_name, output_format, inheritance_key)
            else:
                if os.path.exists(file_path):
                    # need to append a cachebust as per static_asset
                    to_output = output_format % os.path.join(media_url, file_name)
                    output += to_output
                else:
                    raise template.TemplateSyntaxError, "%s does not exist" % file_path
    else:
        filename = FILE_VERSIONS[inheritance_key][parent_name]
        if gzipped:
            filename = "%s.jgz" % filename  # Old versions of Safari have issues with .gz, so now switching to .jgz
        output = output_format % os.path.join(media_url, filename)
    return output
