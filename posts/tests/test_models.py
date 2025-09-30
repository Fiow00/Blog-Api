from django.test import TestCase

from django.contrib.auth import get_user_model

from posts.models import *

class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username = "testuser",
            email = "test@email.com",
            password = "secret",
        )

        cls.post = Post.objects.create(
            author = cls.user,
            title = "A good title",
            body = "Nice body content",
        )

    def test_user_creation(self):
        """Test that a user can be created successfully"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@email.com")

    def test_post_creation(self):
        """Test that a post can be created successfully"""
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.title, "A good title")
        self.assertEqual(self.post.body, "Nice body content")

    def test_post_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.post), "A good title")