from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.models import TrafficViolation, MediaFile
from reports.views import dashboard

# Create your tests here.

class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.factory = RequestFactory()

    def add_messages_to_request(self, request):
        # Attach the messages framework to the request
        # Necessary because the RequestFactory class doesn't support middleware.
        messages_storage = FallbackStorage(request)
        request._messages = messages_storage

    def test_file_saving(self):
        # TODO: Implement the file saving test case
        pass

    def test_mediafile_instance_creation(self):
        # TODO: Implement the MediaFile instance creation test case
        pass

    def test_success_message(self):
        # TODO: Implement the success message test case
        pass
