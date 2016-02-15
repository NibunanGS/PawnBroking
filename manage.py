#!/usr/bin/env python
import os
import sys

# Comment out, if you don't want debugging...
# sys.path.append(r'/Applications/eclipse/plugins/org.python.pydev_2.8.1.2013072611/pysrc')

# import pydevd
# pydevd.patch_django_autoreload(patch_remote_debugger=True, patch_show_console=False)
# -- Debugging setting ends...


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mybusiness.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
