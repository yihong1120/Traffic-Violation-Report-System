"""
This file contains utility functions for creating mock objects for testing purposes in the Traffic Violation Report System.
"""

import unittest
from unittest.mock import MagicMock

from django.test import RequestFactory


def create_mock_request(method, url, data=None):
    """
    Creates a mock request object for testing purposes.

    Parameters:
    method (str): The HTTP method of the request.
    url (str): The URL of the request.
    data (dict, optional): The data of the request. Defaults to None.

    Returns:
    Request: A mock request object.
    """
    mock_request = RequestFactory().generic(method, url, data=data)
    return mock_request


def create_mock_traffic_violations(num_violations, attributes=None):
    """
    Creates a list of mock traffic violation objects for testing purposes.

    Parameters:
    num_violations (int): The number of mock traffic violation objects to create.
    attributes (dict, optional): A dictionary of attributes to set on the mock objects. Defaults to None.

    Returns:
    list: A list of mock traffic violation objects.
    """
    mock_traffic_violations = [MagicMock() for _ in range(num_violations)]
    if attributes:
        for violation in mock_traffic_violations:
            for attr, value in attributes.items():
                setattr(violation, attr, value)
    return mock_traffic_violations


def create_mock_media_files(num_files, attributes=None):
    """
    Creates a list of mock media file objects for testing purposes.

    Parameters:
    num_files (int): The number of mock media file objects to create.
    attributes (dict, optional): A dictionary of attributes to set on the mock objects. Defaults to None.

    Returns:
    list: A list of mock media file objects.
    """
    mock_media_files = [MagicMock() for _ in range(num_files)]
    if attributes:
        for file in mock_media_files:
            for attr, value in attributes.items():
                setattr(file, attr, value)
    return mock_media_files
