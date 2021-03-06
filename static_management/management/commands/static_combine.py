import codecs
import os
from os.path import relpath
import subprocess
import datetime
import re

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from static_management import settings
from static_management.utils import get_versioner
from static_management.models import FileVersion

import logging
logger = logging.getLogger(settings.STATIC_MANAGEMENT_LOGGER)

try:
    CSS_ASSET_PATTERN = re.compile(settings.STATIC_MANAGEMENT_CSS_ASSET_PATTERN)
except AttributeError:
    CSS_ASSET_PATTERN = re.compile('(?P<url>url(\([\'"]?(?P<filename>[^)]+\.[a-z]{3,4})(?P<fragment>#\w+)?[\'"]?\)))')


class Command(BaseCommand):
    """static management commands for static_combine argument"""

    option_list = BaseCommand.option_list + (
        make_option("-c", "--no-compress", action="store_false", dest="compress", default=True, help='Runs the compression script defined in "STATIC_MANAGEMENT_COMPRESS_CMD" on the final combined files'),
        make_option("-s", "--no-sync", action="store_false", dest="sync", default=True, help='Outputs the list of filenames with version info using the "STATIC_MANAGEMENT_VERSION_OUTPUT"'),
    )

    def handle(self, *args, **kwargs):
        self.options = kwargs
        self.css_files = []
        self.combine_js()
        self.combine_css()
        if self.options['sync'] and settings.STATIC_MANAGEMENT_SYNC_COMMAND:
            call_command(settings.STATIC_MANAGEMENT_SYNC_COMMAND, **settings.STATIC_MANAGEMENT_SYNC_COMMAND_KWARGS)

    def combine_js(self):
        logger.info("Combining js....")
        try:
            js_files = settings.STATIC_MANAGEMENT['js']
        except AttributeError:
            logger.warning("Static JS files not provided")
            js_files = None
        if js_files:
            combine_files(js_files, self.options)

    def combine_css(self):
        logger.info("Combining css....")
        try:
            css_files = settings.STATIC_MANAGEMENT['css']
        except AttributeError:
            logger.warning("Static CSS files not provided.")
            css_files = None
        combine_files(css_files, self.options)
        for file in css_files:
            self.css_files.append(file)


def finditer_replace(reg, replace_function, text):
    reg = re.compile(reg)
    cursor_pos = 0
    output = []
    for match in reg.finditer(text):
        output.append(text[cursor_pos:match.start(0)])
        output.append(replace_function(match))
        cursor_pos = match.end(0)
    output.append(text[cursor_pos:])
    return ''.join(output)


def make_css_urls_absolute(filename, file_contents):

    def abs_path(match):
        grp = match.groupdict()
        relative_filename = relpath(filename, settings.STATIC_MANAGEMENT_ROOT)
        relative_dirname = os.path.dirname(relative_filename)
        absolute_path = '/{}/{}{}'.format(relative_dirname, grp['filename'], grp.get('fragment') or '')
        return 'url({})'.format(os.path.abspath(absolute_path))

    return finditer_replace(CSS_ASSET_PATTERN, abs_path, file_contents)


def combine_files(files, options):
    for main_file in files:
        contained_files = files[main_file]
        if not is_modified(main_file, contained_files):
            logging.info("Skipping static_combine for files under %s since none of them have been modified", main_file)
            continue
        to_combine = recurse_files(main_file, contained_files, files)
        to_combine_paths = [os.path.join(settings.STATIC_MANAGEMENT_ROOT, f_name) for f_name in to_combine if os.path.exists(os.path.join(settings.STATIC_MANAGEMENT_ROOT, f_name))]
        logging.info("Building %s" % main_file)
        static_combine(main_file, to_combine_paths, compress=options['compress'])


def is_modified(file_key, files):
    file_version, created = FileVersion.objects.get_or_create(file_key=file_key)
    if created:
        return True

    db_file_ts = file_version.datetime
    for the_file in files:
        path_to_file = os.path.join(settings.STATIC_MANAGEMENT_ROOT, the_file)
        if os.path.isfile(path_to_file):
            system_file_ts = datetime.datetime.fromtimestamp(os.path.getmtime(path_to_file))
            if system_file_ts > db_file_ts:
                return True
    return False


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


def static_combine(end_file_key, to_combine, delimiter=u"\n/* Begin: %s */\n", compress=False):
    """joins paths together to create a single file

    Usage: static_combine(my_ultimate_file, list_of_paths, [delimiter])

    delimiter is set to a Javascript and CSS safe comment to note where files
    start"""
    end_file = os.path.join(settings.STATIC_MANAGEMENT_ROOT, end_file_key)
    combo_file = codecs.open(end_file, "w", "utf-8")
    to_write = u''
    for static_file in to_combine:
        if os.path.isfile(static_file):
            logger.debug('Reading %s' % static_file)
            if delimiter:
                to_write += delimiter % os.path.split(static_file)[1]

            file_contents = codecs.open(static_file, "r", "utf-8").read()
            file_contents = make_css_urls_absolute(static_file, file_contents)
            to_write += file_contents
        else:
            logger.warning('%s is not a file!' % static_file)
    if to_write:
        logging.debug('Writing %s' % end_file)
        combo_file.write(to_write)
        combo_file.close()
        if compress:
            try:
                command = settings.STATIC_MANAGEMENT_COMPRESS_CMD % end_file
            except AttributeError:
                raise CommandError("STATIC_MANAGEMENT_COMPRESS_CMD not set")
            except TypeError:
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
            end_file = os.path.join(settings.STATIC_MANAGEMENT_ROOT, file_version.filename)
            logging.debug('Writing %s' % end_file)
            combo_file = open(end_file, 'w')
            combo_file.write(to_write)
            combo_file.close()
