#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    if os.environ.get("JYTHON_PATH"): sys.path.append(os.environ.get("JYTHON_PATH"))
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'lib-python'))

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
