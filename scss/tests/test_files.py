"""Evaluates all the tests that live in `scss/tests/files`.

A test is any file with a `.scss` extension.  It'll be compiled, and the output
will be compared to the contents of a file named `foo.css`.

Currently, test files must be nested exactly one directory below `files/`.
This limitation is completely arbitrary. Files starting with '_' are skipped.

"""

from __future__ import absolute_import, unicode_literals

import os
import logging
import sys
from importlib import import_module

import six

import scss


if six.PY2:
    from io import open


console = logging.StreamHandler()
logger = logging.getLogger('scss')
logger.setLevel(logging.ERROR)
logger.addHandler(console)


def test_pair_programmatic(scss_file_pair):
    scss_fn, css_fn = scss_file_pair

    # look for a python module related to the pair and execute it if found
    mod = None
    cfg_script = scss_fn.replace('.scss', '.py')
    if os.path.exists(cfg_script):
        sys.path[0:0] = [os.path.dirname(scss_fn)]
        mod = import_module(os.path.splitext(os.path.split(scss_fn)[1])[0])
        getattr(mod, 'setUp', lambda: None)()
        sys.path = sys.path[1:]

    with open(scss_fn) as fh:
        source = fh.read()
    with open(css_fn, 'r', encoding='utf8') as fh:
        expected = fh.read()

    directory, _ = os.path.split(scss_fn)
    include_dir = os.path.join(directory, 'include')
    scss.config.STATIC_ROOT = os.path.join(directory, 'static')

    try:
        compiler = scss.Scss(scss_opts=dict(style='expanded'), search_paths=[include_dir, directory])
        actual = compiler.compile(source)

        getattr(mod, 'tearDown', lambda:None)()

        # Normalize leading and trailing newlines
        actual = actual.strip('\n')
        expected = expected.strip('\n')

        assert expected == actual

    finally:
        # cleanup generated assets if any
        assets_dir = os.path.join(directory, 'static', 'assets')
        if os.path.isdir(assets_dir):
            for x in os.listdir(assets_dir):
                if x != '.placeholder':
                    os.remove(os.path.join(assets_dir, x))

def test_rel_import():

    scss_vars = {}
    _scss = scss.Scss(scss_vars=scss_vars)

    actual = _scss.compile(scss_file=os.path.join(os.path.dirname(__file__),
                                                  'files', 'general',
                                                  'relative-import.fscss'))

    expected = open(os.path.join(os.path.dirname(__file__), 'files',
                                 'general', 'relative-import.css')).read()

    assert expected == actual
