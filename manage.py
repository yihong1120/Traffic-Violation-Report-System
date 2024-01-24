#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Set the DJANGO_SETTINGS_MODULE only if the application is not stopped
    if os.environ.get('DJANGO_SETTINGS_MODULE') is None and os.environ.get('APP_ENGINE_ENVIRONMENT') != 'stopped':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrafficViolationReport.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
