from static_management import settings

def get_versioner(versioner=settings.STATIC_MANAGEMENT_VERSIONER):
    """gets the file version based on the versioner provided"""
    try:
        dot = versioner.rindex('.')
    except ValueError:
        raise exceptions.ImproperlyConfigured, '%s isn\'t a versioner' % versioner
    v_module, v_classname = versioner[:dot], versioner[dot+1:]
    try:
        mod = __import__(v_module, {}, {}, [''])
    except ImportError, e:
        raise exceptions.ImproperlyConfigured, 'Error importing versioner %s: "%s"' % (v_module, e)
    try:
        v_class = getattr(mod, v_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured, 'Versioner module "%s" does not define a "%s" class' % (v_module, v_classname)
    return v_class()
