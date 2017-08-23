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
    return make_parser().parse_args(args)


def runtests():
    args = parse_args()

    if args.deprecation == 'all':
        # Show all deprecation warnings from all packages
        warnings.simplefilter('default', category=DeprecationWarning)
        warnings.simplefilter('default', category=PendingDeprecationWarning)
    elif args.deprecation == 'pending':
        # Show all deprecation warnings
        warnings.filterwarnings('default', category=DeprecationWarning)
        warnings.filterwarnings('default', category=PendingDeprecationWarning)
    elif args.deprecation == 'imminent':
        # Show only imminent deprecation warnings
        warnings.filterwarnings('default', category=DeprecationWarning)
    elif args.deprecation == 'none':
        # Deprecation warnings are ignored by default
        pass

    argv = [sys.argv[0], 'test']
    return execute_from_command_line(argv)
    
if __name__ == '__main__':
    sys.exit(runtests())
