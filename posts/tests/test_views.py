from django.test import TestCase

from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from posts.models import Post

class PostViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            username = "author1",
            email = "author1@email.com",
            password = "testing321",
        )

        cls.user2 = get_user_model().objects.create_user(
            username = "author2",
            email = "author2@email.com",
            password = "testing321",
        )

        cls.post1 = Post.objects.create(
            title = "First post",
            body = "Content of first post",
            author = cls.user1,
        )

        cls.post2 = Post.objects.create(
            title = "Second post",
            body = "Content of second post",
            author = cls.user2,
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user1)

    def test_get_all_posts(self):
        """READ Test - gets all posts without modifying them"""
        url = reverse("post_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Should return 2 posts from setUpTestData

        post_titles = [post['title'] for post in response.data]
        self.assertIn("First post", post_titles)
        self.assertIn("Second post", post_titles)

    def test_get_single_post(self):
        """READ Test - gets a single post without modifying it"""
        url = reverse("post_detail", kwargs={"pk": self.post1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "First post")
        self.assertEqual(response.data["body"], "Content of first post")
        self.assertEqual(response.data["author"], self.user1.id)

    def test_create_post(self):
        """CREATE Test - makes a new post (modifies database)"""
        url = reverse("post_list")
        data = {
            "title": "Brand New Post via API",
            "body": "This is created via API test",
            "author": self.user1.id,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should now have 3 posts (2 from setUpTestData + 1 new)
        self.assertEqual(Post.objects.count(), 3)
        self.assertEqual(Post.objects.latest("id").title, "Brand New Post via API")

    def test_update_post(self):
        """UPDATE Test - modifies existing post"""
        url = reverse("post_detail", kwargs={"pk": self.post1.id})
        data = {
            "title": "Updated post title",
            "body": "Updated content",
            "author": self.user1.id
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database and verify changes
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "Updated post title")
        self.assertEqual(self.post1.body, "Updated content")

    def test_partial_update_post(self):
        """PARTIAL UPDATE Test - modified only some fields"""
        url = reverse("post_detail", kwargs={"pk": self.post1.id})
        data = {
            "title": "Partially updated title",
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "Partially updated title")
        # Body should remain unchanged from setUpTestData
        self.assertEqual(self.post1.body, "Content of first post")

    def test_delete_post(self):
        """DELETE Test - removes a post (modifies database)"""
        url = reverse("post_detail", kwargs={"pk": self.post1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should now have 1 post (Post2 remains)
        self.assertEqual(Post.objects.count(), 1)

        # Verify post1 is gone
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=self.post1.id)


