#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# webmacs documentation build configuration file, created by
# sphinx-quickstart on Sat Dec 23 08:47:03 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.join(os.path.abspath("."), "ext"))
sys.path.insert(0, os.path.abspath('..'))

# Generating doc don't work without that flag. That could be fixed but anyway
# on readthedocs we can't install binary package so we are stuck for now trying
# to mock everything.
if True or "READTHEDOCS" in os.environ:
    # We can not install webmacs on readthedocs, as it requires to
    # buid some C extensions (from dateparser, PyQt5, ...). The
    # alternative is to mock any dependency used by webmacs.

    class Mock(object):
        def __init__(self, *a, **kw):
            pass
        def __getattr__(self, name):  # noqa: E301
            return Mock()
        def __call__(self, *a, **kw):  # noqa: E301
            return Mock()
        def __iter__(self):  # noqa: E301
            return iter(())
        def __instancecheck__(self, instance):  # noqa: E301
            return True
        def __subclasscheck__(self, cls):  # noqa: E301
            return True
        def __mro_entries__(self, a):  # noqa: E301
            return ()

    MOCK_MODULES = ["PyQt5", "PyQt5.QtCore", "PyQt5.QtGui",
                    "PyQt5.QtWidgets", "PyQt5.QtWebEngineWidgets",
                    "PyQt5.QtWebEngineCore", "PyQt5.QtWebChannel",
                    "PyQt5.QtNetwork",
                    "_adblock", "dateparser"]
    sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)
    # the version number is not important, though it must be an int.
    sys.modules["PyQt5.QtCore"].QT_VERSION \
        = sys.modules["PyQt5.QtCore"].PYQT_VERSION = 330497

import webmacs  # noqa: E402


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode', "webmacs_sphinx_ext"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'webmacs'
copyright = '2017, Julien Pagès'
author = 'Julien Pagès'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = webmacs.__version__
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'github_user': 'parkouss',
    'github_repo': project,
    "github_button": True,
    'description': "An emacs-like keyboard-driven web browser",
    # defaults is 940, gives a bit more so viewcode looks good.
    'page_width': "1050px",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'webmacsdoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'webmacs.tex', 'webmacs Documentation',
     'Julien Pagès', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'webmacs', 'webmacs Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'webmacs', 'webmacs Documentation',
     author, 'webmacs', 'One line description of project.',
     'Miscellaneous'),
]
