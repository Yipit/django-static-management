Static Management
=================

## CHANGES in our fork:

### Base path for the relative static files

All the files are relative to `settings.STATIC_MANAGEMENT_ROOT` by
default, but [if that setting is not defined, then it will fallback](https://github.com/Yipit/django-static-management/blob/f4a2151642a349e2d793a4fbe3b12da2866c76cb/static_management/settings.py#L28) to
`settings.MEDIA_ROOT`.

#### Example:

In your `settings.py` file.

```python
from os.path import dirname, abspath, join

STATIC_MANAGEMENT_ROOT = join(abspath(dirname(__file__)), "apps", "yipit-static-media", "static")
```

### CSS regular expression pattern

In our fork we
[**ALWAYS**](https://github.com/Yipit/django-static-management/commit/6719bee2ad971016153347c2e984975d1afc25f8)
use the dajngo setting `STATIC_MANAGEMENT_CSS_ASSET_PATTERN` to find
the url, filename and fragment.

This project is intended as an easy way to manage multiple static text
assets (CSS and Javascript) in a Django projects.

Currently includes:
-------------------

* JS and CSS template tags -- one link to the concatenated file for production, links too all files when DEBUG = True for easy development;
* A Django management command to combine files (with support for compression and syncing);
* Support for command line minification/compression when building (YUI compressor, JSMin, Icy etc.).
* Support for filename versioning (using SHA1 sums, file modification times, etc.).

Usage
-----

The configuration is intended to be easy to read and use.

Add the `static_management` directory into your Django application, and included it in `installed_apps`.

You can include the current version as a `git submodule` as follows:

    git submodule add git://github.com/bradleywright/django-static-management.git django_site_dir/static_management

Substitute `django_site_dir` with the root directory of your Django application (where `manage.py` and `settings.py` live).

### Settings

Add the following construct (or similar) in `settings.py`:

    STATIC_MANAGEMENT = {
        'css': {
            'css/mymainfile.css' : [
                'css/myfile.css',
                'css/anotherfile.css'
            ],
        },
        'js': {
            'js/myjsfile.js' : [
                'js/mynewfile.js',
                'js/anotherfile.js'
            ],
        }
    }

What happens is that files inside `css` and `js` are combined as follows:

1. `css/mymainfile.css` (the "key" of the key/value pair) is the target file, which is created automatically from the list of files (the "value" of the key/value pair) beside it;
2. If the files do not exist, the entire file is skipped;
3. Paths are *relative* to `settings.STATIC_MEDIA_ROOT`, but if it's not defined, it will fallback to `settings.MEDIA_ROOT` (so you're unlikely to need to move files around in an already working Django project).
4. The combined css file should be in the same directory as the files it's constructed from.

Other files may inherit from `css/mymainfile.css` (for example, IE hack files) by including it in their list of files, like so:

    ...
    'css/myie6.css' : [
        'css/mymainfile.css', # inherits from main
        'css/ie6.css'
    ]
    ...

### Templates

In your templates, you use the `static_combo` and `static_asset` template tag libraries:

    {% load static_combo %}
    {% static_combo_css "css/mymainfile.css" %}
    {% static_combo_js "js/myjsfile.js" %}

Where `css/mymainfile.css` is the "combined" file name from your settings. In `DEBUG` mode, this will echo out all the files in order (for debugging purposes). In production mode, it will only echo the "combined" file name.

By default the CSS template tag uses HTML 4.01 style `link` elements (non self-closing) - you may override this with a setting like:

    STATIC_MANAGEMENT_CSS_LINK = '<link rel="stylesheet" type="text/css" href="%s" />\n'

The Javascript template tag uses the standard construct, and only needs to be overridden if you want to force UTF-8 encoding in your files:

    STATIC_MANAGEMENT_SCRIPT_SRC = '<script type="text/javascript" charset="utf-8" src="%s"></script>\n'

### File versioning

In order to help meet [performance recommendations](http://developer.yahoo.net/blog/archives/2007/05/high_performanc_2.html) which encourage the use of `Expires:` headers, static management supports versioning files.

To use, simply define a dictionary that maps relative filenames to versioned filenames:

    STATIC_MANAGEMENT_VERSIONS = {
        'js/main.js': 'http://cdn1.example.com/js/main.15274671.js',
        'js/main.css': 'http://cdn2.example.com/js/main.82773622.css',
        'img/logo.png': 'http://cdn1.example.com/img/logo.99182772.png',
        'img/icon.png': 'http://cdn2.example.com/img/icon.31901927.png'
    }


#### Version class

Specify the type of file versioning with a setting like:

    STATIC_MANAGEMENT_VERSIONER = 'static_management.versioners.SHA1Sum'

The following pre-rolled versioners are included:

* `SHA1Sum` - Calculates the SHA1 sum of a file's contents and uses the first 8 characters for the version
* `MD5Sum` - Same as `SHA1Sum` but using the MD5 algorithm instead
* `FileTimestamp` - Uses the UNIX time representation of the file modification time to generate a version

Custom versioners are simple callables that take a single filename argument.

### Management commands

The following command will generate all the files as per your settings:

    ./manage.py static_combine

#### Compression

Passing an argument of `--compress` to the above command will run the compression script of your choice, as specified in: `settings.STATIC_MANAGEMENT_COMPRESS_CMD`. This should be a string representing the script you want to run. The only caveat is that it must accept a filepath as an argument and return output to `stdout` (the management command reads from `stdout`). Following is an example using YUI Compressor (which this command was designed to use):

    # settings.py
    STATIC_MANAGEMENT_COMPRESS_CMD = 'java -jar /home/myuser/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar %s'

where `%s` represents the path of the file to be compressed.

Using this within a Django project
----------------------------------

The [1.0 tag](http://github.com/bradleywright/django-static-management/tree/1.0) of this project contains a sample Django project to help demonstrate usage. This code structure will not be followed beyond the initial version--a `git submodule` is now the preferred way of using this application.

License
-------

This work contains some samples of the [YUI](http://developer.yahoo.com/yui/) library, which is licensed under a [BSD License](http://developer.yahoo.com/yui/license.html). My own work here is licensed similarly.
