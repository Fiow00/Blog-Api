from django.test import TestCase

from django.contrib.auth import get_user_model

from posts.serializers import *
from posts.models import *

class PostSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username = "testuser",
            email = "test@email.com",
            password = "secret",
        )

        cls.post_data = {
            "title": "Test Post",
            "body": "Test content for serializer",
            "author": cls.user.id,
        }

    def test_serializer_with_valid_data(self):
        serializer = PostSerializer(data=self.post_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_invalid_data(self):
        invalid_data = {
            "title": "", # Empty title should be invalid
            "body": "Test body",
            "author": self.user.id,
        }
        serializer = PostSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serializer_fields(self):
        serializer = PostSerializer()
        expected_fields = ["id", "author", "title", "body", "created_at"]
        self.assertEqual(list(serializer.fields.keys()), expected_fields)