#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(project_dir, '.env'))
    src_path = os.path.join(project_dir, '..', 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

