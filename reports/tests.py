from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from reports.models import TrafficViolation, MediaFile
from reports.views import dashboard, search_traffic_violations_view, traffic_violation_markers_view, traffic_violation_details_view

# Create your tests here.

class SearchTrafficViolationsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.traffic_violation_one = TrafficViolation.objects.create(
            license_plate='ABC123',
            violation='闖紅燈',
            status='通過',
            location='Test Location',
            officer=self.user
        )
        self.media_file_one = MediaFile.objects.create(
            traffic_violation=self.traffic_violation_one,
            file=SimpleUploadedFile('test_media.jpg', b'test content', content_type='image/jpeg')
        )

    def test_search_traffic_violations_view_scenarios(self):
        # Test the search_traffic_violations_view function with different parameters and scenarios
        request = self.factory.get('/search/', {'query': 'ABC123'})
        request.user = self.user
        response = search_traffic_violations_view(request)
        self.assertEqual(response.status_code, 200)
        # Add more assertions and scenarios as needed

    def tearDown(self):
        self.user.delete()
        self.traffic_violation_one.delete()
        self.media_file_one.delete()

class TrafficViolationMarkersViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.traffic_violation_two = TrafficViolation.objects.create(
            license_plate='XYZ789',
            violation='行駛人行道',
            status='未通過',
            location='Another Test Location',
            officer=self.user
        )

    def test_traffic_violation_markers_view_scenarios(self):
        # Test the traffic_violation_markers_view function with different scenarios
        request = self.factory.get('/markers/')
        request.user = self.user
        response = traffic_violation_markers_view(request)
        self.assertEqual(response.status_code, 200)
        # Add more assertions and scenarios as needed

    def tearDown(self):
        self.user.delete()
        self.traffic_violation_two.delete()

class TrafficViolationDetailsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.traffic_violation_three = TrafficViolation.objects.create(
            license_plate='LMN456',
            violation='未禮讓直行車',
            status='其他',
            location='Additional Test Location',
            officer=self.user
        )
        self.media_file_two = MediaFile.objects.create(
            traffic_violation=self.traffic_violation_three,
            file=SimpleUploadedFile('another_test_media.jpg', b'another test content', content_type='image/jpeg')
        )

    def test_traffic_violation_details_view_scenarios(self):
        # Test the traffic_violation_details_view function with different scenarios
        request = self.factory.get(f'/details/{self.traffic_violation_three.pk}/')
        request.user = self.user
        response = traffic_violation_details_view(request, pk=self.traffic_violation_three.pk)
        self.assertEqual(response.status_code, 200)
        # Add more assertions and scenarios as needed

    def tearDown(self):
        self.user.delete()
        self.traffic_violation_three.delete()
        self.media_file_two.delete()

class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.factory = RequestFactory()

    def add_messages_to_request(self, request):
        messages_storage = FallbackStorage(request)
        request._messages = messages_storage

    def test_file_saving(self):
        # Implement the file saving test case
        request = self.factory.post('/dashboard/', data={
            'file': SimpleUploadedFile('new_test_media.jpg', b'new test content', content_type='image/jpeg')
        })
        request.user = self.user
        self.add_messages_to_request(request)
        response = dashboard(request)
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful file upload
        # Check if the file was saved correctly
        self.assertTrue(MediaFile.objects.filter(file='new_test_media.jpg').exists())

    def test_mediafile_instance_creation(self):
        # Implement the MediaFile instance creation test case
        traffic_violation = TrafficViolation.objects.create(
            license_plate='TEST123',
            violation='Test Violation',
            status='Test Status',
            location='Test Location',
            officer=self.user
        )
        media_file = MediaFile.objects.create(
            traffic_violation=traffic_violation,
            file=SimpleUploadedFile('test_media_instance.jpg', b'test content', content_type='image/jpeg')
        )
        self.assertTrue(isinstance(media_file, MediaFile))
        self.assertEqual(media_file.traffic_violation, traffic_violation)

    def test_success_message(self):
        # Implement the success message test case
        request = self.factory.post('/dashboard/', data={
            'file': SimpleUploadedFile('new_test_media.jpg', b'new test content', content_type='image/jpeg')
        })
        request.user = self.user
        self.add_messages_to_request(request)
        dashboard(request)
        # Check if the success message was added to the request
        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The record and media files have been successfully updated.")

    def tearDown(self):
        self.user.delete()
        MediaFile.objects.all().delete()
        TrafficViolation.objects.all().delete()