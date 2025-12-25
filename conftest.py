import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# --- The Wrapper Logic ---

class SREClientWrapper:
    """
    Internal wrapper to ensure all test requests follow SRE standards
    and fail early on routing errors.
    """
    def __init__(self, client):
        self.client = client

    def _request(self, method, url, *args, **kwargs):
        func = getattr(self.client, method)
        response = func(url, *args, **kwargs)

        # Global 404 Protection
        if response.status_code == 404:
            pytest.fail(f"❌ Route Failure: The URL '{url}' does not exist on the server. Check your urls.py or test path.")
        
        return response

    def get(self, url, *args, **kwargs): return self._request('get', url, *args, **kwargs)
    def post(self, url, *args, **kwargs): return self._request('post', url, *args, **kwargs)
    def put(self, url, *args, **kwargs): return self._request('put', url, *args, **kwargs)
    def patch(self, url, *args, **kwargs): return self._request('patch', url, *args, **kwargs)
    def delete(self, url, *args, **kwargs): return self._request('delete', url, *args, **kwargs)


# --- Reusable User Fixtures ---

@pytest.fixture
def user1(db):
    return User.objects.create_user(email="shristi500@gmail.com", password="Gwen@12345")

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(email="admin@user.com", password="Admin@1234")


@pytest.fixture
def user2(db):
    return User.objects.create_user(email="strela500@gmail.com", password="Gwen@12345")


@pytest.fixture
def user1_client(user1):
    """Authenticated and Wrapped client for user1"""
    client = APIClient()
    refresh = RefreshToken.for_user(user1)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    # We wrap it here before returning
    return SREClientWrapper(client)


@pytest.fixture
def user2_client(user2):
    """Authenticated and Wrapped client for user2"""
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    # We wrap it here before returning
    return SREClientWrapper(client)

@pytest.fixture
def admin_client(admin_user):
    """Authenticated and Wrapped client for admin"""
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    # We wrap it here before returning
    return SREClientWrapper(client)

@pytest.fixture
def anon_client():
    """Unauthenticated but still Wrapped client for testing permissions"""
    return SREClientWrapper(APIClient())


@pytest.fixture
def dummy_image():
    """Generates a tiny valid JPEG image in memory for testing uploads."""
    # Minimal valid JPEG: 1x1 pixel red image
    jpeg_data = (
        b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x00\x00\x01'
        b'\x00\x01\x00\x00\xFF\xDB\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08'
        b'\x07\x07\x07\x09\x09\x08\x0A\x0C\x14\x0D\x0C\x0B\x0B\x0C\x19\x12'
        b'\x13\x0F\x14\x1D\x1A\x1F\x1E\x1D\x1A\x1C\x1C\x20\x24\x2E\x27\x20'
        b'\x22\x2C\x23\x1C\x1C\x28\x37\x29\x2C\x30\x31\x34\x34\x34\x1F\x27'
        b'\x39\x3D\x38\x32\x3C\x2E\x33\x34\x32\xFF\xC0\x00\x0B\x08\x00\x01'
        b'\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01'
        b'\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04'
        b'\x05\x06\x07\x08\x09\x0A\x0B\xFF\xC4\x00\xB5\x10\x00\x02\x01\x03'
        b'\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01\x7D\x01\x02\x03\x00'
        b'\x04\x11\x05\x12\x21\x31\x41\x06\x13\x51\x61\x07\x22\x71\x14\x32'
        b'\x81\x91\xA1\x08\x23\x42\xB1\xC1\x15\x52\xD1\xF0\x24\x33\x62\x72'
        b'\x82\x09\x0A\x16\x17\x18\x19\x1A\x25\x26\x27\x28\x29\x2A\x34\x35'
        b'\x36\x37\x38\x39\x3A\x43\x44\x45\x46\x47\x48\x49\x4A\x53\x54\x55'
        b'\x56\x57\x58\x59\x5A\x63\x64\x65\x66\x67\x68\x69\x6A\x73\x74\x75'
        b'\x76\x77\x78\x79\x7A\x83\x84\x85\x86\x87\x88\x89\x8A\x92\x93\x94'
        b'\x95\x96\x97\x98\x99\x9A\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xB2'
        b'\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xC2\xC3\xC4\xC5\xC6\xC7\xC8\xC9'
        b'\xCA\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xE1\xE2\xE3\xE4\xE5\xE6'
        b'\xE7\xE8\xE9\xEA\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFF\xDA'
        b'\x00\x08\x01\x01\x00\x00\x3F\x00\xFE\xA2\x8A\xFF\xD9'
    )
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=jpeg_data,
        content_type='image/jpeg'
    )


@pytest.fixture
def dummy_images(dummy_image):
    """Returns a list of dummy images for bulk upload testing."""
    images = []
    for i in range(3):
        dummy_image.seek(0)  # Reset file pointer
        image_data = dummy_image.read()
        images.append(SimpleUploadedFile(
            name=f'test_image_{i}.jpg',
            content=image_data,
            content_type='image/jpeg'
        ))
        dummy_image.seek(0)  # Reset file pointer for reuse
    return images