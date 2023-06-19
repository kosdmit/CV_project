from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from io import BytesIO

from app_resume.tests.test_mixins import CreateMethodsMixin
from app_social.models import Post
from app_social.tests.test_mixins import BaseSetUpMixin


class PostModelTest(BaseSetUpMixin, CreateMethodsMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.image_file = BytesIO()
        image = Image.new('RGBA', size=(3000, 3000), color=(156, 156, 156))
        image.save(self.image_file, 'png')
        self.image_file.name = 'test.png'
        self.image_file.seek(0)

    def test_create_post(self):
        post = Post.objects.create(resume=self.resume,
                                   message='Test Post',
                                   image=SimpleUploadedFile(self.image_file.name,
                                                            self.image_file.read()))

        # Validate image compression, image width should be 642
        image = Image.open(post.image)
        self.assertEqual(image.width, 642)
        image.close()

    def test_delete_post(self):
        post = Post.objects.create(resume=self.resume, message='Test Post',
                                   image=SimpleUploadedFile(self.image_file.name,
                                                            self.image_file.read()))

        # Make sure post is created
        self.assertEqual(Post.objects.count(), 1)

        image_path = post.image.name
        post.delete()

        # Validate that the post was deleted
        self.assertEqual(Post.objects.count(), 0)

        # Validate that the image file was deleted
        self.assertFalse(post.image.storage.exists(image_path))

    def tearDown(self):
        self.resume.delete()