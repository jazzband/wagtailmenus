#!/usr/bin/env python
import argparse
import os
import sys
import warnings

from django.core.management import execute_from_command_line

os.environ['DJANGO_SETTINGS_MODULE'] = 'wagtailmenus.settings.testing'


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--deprecation',
        choices=['all', 'pending', 'imminent', 'none'],
        default='imminent'
    )
    return parser


def parse_args(args=None):
    return make_parser().parse_known_args(args)


def runtests():
    parsed_args, unparsed_args = parse_args()

    only_wagtailmenus = r'^wagtailmenus(\.|$)'
    if parsed_args.deprecation == 'all':
        # Show all deprecation warnings from all packages
        warnings.simplefilter('default', category=DeprecationWarning)
        warnings.simplefilter('default', category=PendingDeprecationWarning)
    elif parsed_args.deprecation == 'pending':
        # Show all deprecation warnings
        warnings.filterwarnings('default', category=DeprecationWarning, module=only_wagtailmenus)
        warnings.filterwarnings('default', category=PendingDeprecationWarning, module=only_wagtailmenus)
    elif parsed_args.deprecation == 'imminent':
        # Show only imminent deprecation warnings
        warnings.filterwarnings('default', category=DeprecationWarning, module=only_wagtailmenus)
    elif parsed_args.deprecation == 'none':
        # Deprecation warnings are ignored
        pass

    argv = [sys.argv[0], 'test'] + unparsed_args
    return execute_from_command_line(argv)

if __name__ == '__main__':
    sys.exit(runtests())
