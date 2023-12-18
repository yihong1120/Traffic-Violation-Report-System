import unittest
from unittest.mock import MagicMock

from django.test import RequestFactory


def create_mock_request(method, url, data=None):
    mock_request = RequestFactory().generic(method, url, data=data)
    return mock_request

def create_mock_traffic_violations(num_violations, attributes=None):
    mock_traffic_violations = [MagicMock() for _ in range(num_violations)]
    if attributes:
        for violation in mock_traffic_violations:
            for attr, value in attributes.items():
                setattr(violation, attr, value)
    return mock_traffic_violations

def create_mock_media_files(num_files, attributes=None):
    mock_media_files = [MagicMock() for _ in range(num_files)]
    if attributes:
        for file in mock_media_files:
            for attr, value in attributes.items():
                setattr(file, attr, value)
    return mock_media_files
