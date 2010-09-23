import os
import subprocess

from optparse import OptionParser, make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from static_management import settings
from static_management.utils import get_versioner
from static_management.models import FileVersion

class Command(BaseCommand):
    """static management commands for static_combine argument"""
    
    option_list = BaseCommand.option_list + (
        make_option("-c", "--no-compress", action="store_false", dest="compress", default=True, help='Runs the compression script defined in "STATIC_MANAGEMENT_COMPRESS_CMD" on the final combined files'),
        make_option("-s", "--no-sync", action="store_false", dest="sync", default=True, help='Outputs the list of filenames with version info using the "STATIC_MANAGEMENT_VERSION_OUTPUT"'),
    )
    
    def handle(self, *args, **kwargs):
        self.options = kwargs
        self.files_created = []
        self.combine_js()
        self.combine_css()
        if options['sync']:
            call_command(setting.STATIC_MANAGEMENT_SYNC_COMMAND)
        
    def combine_js(self):
        try:
            js_files = settings.STATIC_MANAGEMENT['js']
        except AttributeError:
            print "Static JS files not provided"
            js_files = None
        if js_files:
            combine_files(js_files, self.options)
            map(self.files_created.append, js_files)
    
    def combine_css(self):
        try:
            css_files = settings.STATIC_MANAGEMENT['css']
        except AttributeError:
            print "Static CSS files not provided."
            css_files = None
        if css_files:
            combine_files(css_files, self.options)
            for css_file in css_files:
                self.files_created.append(css_file)

def combine_files(files, options):
    for main_file in files:
        to_combine = recurse_files(main_file, files[main_file], files)
        to_combine_paths = [os.path.join(settings.MEDIA_ROOT, f_name) for f_name in to_combine if os.path.exists(os.path.join(settings.MEDIA_ROOT, f_name))]
        static_combine(main_file, to_combine_paths, compress=options['compress'])

def recurse_files(name, files, top):
    """
    given following format:
    
    {
        "filename": ["file1", "file2", "file3"],
        "filename2": ["filename", "file4"]
    }
    
    name="filename"
    files=["file1", "file2", "file3"]
    top = Whole dictionary
    
    if a value on the left appears on the right, inherit those files
    """
    combine_files = []
    for to_cat in files:
        if to_cat in top:
            combine_files.extend(recurse_files(to_cat, top[to_cat], top))
        else:
            combine_files.append(to_cat)
    return combine_files


def static_combine(end_file_key, to_combine, delimiter="\n/* Begin: %s */\n", compress=False):
    """joins paths together to create a single file

    Usage: static_combine(my_ultimate_file, list_of_paths, [delimiter])

    delimiter is set to a Javascript and CSS safe comment to note where files 
    start"""
    # FIXME this fails in the face of @import directives in the CSS.
    # a) we need to move all remote @imports up to the top
    # b) we need to recursively expand all local @imports
    end_file = os.path.join(settings.MEDIA_ROOT, end_file_key)
    combo_file = open(end_file, 'w')
    to_write = ''
    for static_file in to_combine:
        if os.path.isfile(static_file):
            if delimiter:
                to_write += delimiter % os.path.split(static_file)[1]
            to_write += file(static_file).read()
    if to_write:
        combo_file.write(to_write)
        combo_file.close()
        if compress:
            try:
                command =  settings.STATIC_MANAGEMENT_COMPRESS_CMD % end_file
            except AttributeError, error:
                raise CommandError("STATIC_MANAGEMENT_COMPRESS_CMD not set")
            except TypeError, error:
                raise CommandError("No string substitution provided for the input file to be passed to the argument ('cmd %s')")
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            to_write = proc.communicate()[0]
            if proc.returncode != 0:
                raise CommandError("STATIC_MANAGEMENT_COMPRESS_CMD failed to run: %s" % command)
        if settings.STATIC_MANAGEMENT_USE_VERSIONS:
            versioner = get_versioner()
            version = versioner(end_file)
            file_version = FileVersion.objects.get_or_create(file_key=end_file_key)[0]
            file_version.version = version
            file_version.compressed = compress
            file_version.save()
            end_file = os.path.join(settings.MEDIA_ROOT, file_version.filename)
        combo_file = open(end_file, 'w')
        combo_file.write(to_write)
        combo_file.close()
        