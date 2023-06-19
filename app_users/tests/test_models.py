from io import BytesIO
from django.test import TestCase

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from app_users.models import Profile


class PostModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='kosdmit', password='testpassword')
        self.model = Profile

        self.image_file = BytesIO()
        image = Image.new('RGBA', size=(3000, 3000), color=(156, 156, 156))
        image.save(self.image_file, 'png')
        self.image_file.name = 'test.png'
        self.image_file.seek(0)
        self.required_image_width = 250

        self.correct_fields = {
            'user': self.user,
            'image': SimpleUploadedFile(self.image_file.name, self.image_file.read())
        }

    def test_create_object(self):
        self.object = self.model.objects.create(**self.correct_fields)

        # Validate image compression, image width should be equal self.required_image_width
        image = Image.open(self.object.image)
        self.assertEqual(image.width, self.required_image_width)
        image.close()

    def test_delete_object(self):
        self.object = self.model.objects.create(**self.correct_fields)

        # Make sure object is created
        self.assertEqual(self.model.objects.count(), 1)

        image_path = self.object.image.name
        self.object.delete()

        # Validate that the post was deleted
        self.assertEqual(self.model.objects.count(), 0)

        # Validate that the image file was deleted
        self.assertFalse(self.object.image.storage.exists(image_path))

    def tearDown(self):
        try:
            self.object.delete()
        except ValueError as e:
            print(e)