from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ..models import Post


class PostViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            username="author1",
            email="author1@email.com",
            password="testing321",
        )

        cls.user2 = get_user_model().objects.create_user(
            username="author2",
            email="author2@email.com",
            password="testing321",
        )

        cls.post1 = Post.objects.create(
            title="First post",
            body="Content of first post",
            author=cls.user1,
        )

        cls.post2 = Post.objects.create(
            title="Second post",
            body="Content of second post",
            author=cls.user2,
        )

    def test_get_all_posts(self):
        """READ Test - gets all posts without modifying them"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Should return 2 posts from setUpTestData

        post_titles = [post['title'] for post in response.data]
        self.assertIn("First post", post_titles)
        self.assertIn("Second post", post_titles)

    def test_get_single_post(self):
        """READ Test - gets a single post without modifying it"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-detail", kwargs={"pk": self.post1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "First post")
        self.assertEqual(response.data["body"], "Content of first post")
        self.assertEqual(response.data["author"], self.user1.id)

    def test_create_post(self):
        """CREATE Test - makes a new post (modifies database)"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-list")
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
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-detail", kwargs={"pk": self.post1.id})
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
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-detail", kwargs={"pk": self.post1.id})
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
        self.client.force_authenticate(user=self.user1)
        url = reverse("posts-detail", kwargs={"pk": self.post1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Should now have 1 post (Post2 remains)
        self.assertEqual(Post.objects.count(), 1)

        # Verify post1 is gone
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=self.post1.id)


class PostAuthorizationTest(APITestCase):
    """Test that users can only modify their own posts"""

    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(
            username="owner",
            email="owner@email.com",
            password="testing321",
        )

        cls.user2 = get_user_model().objects.create_user(
            username="other",
            email="other@email.com",
            password="testing321",
        )

        cls.post1 = Post.objects.create(
            title="owner post",
            body="Content of owner post",
            author=cls.user1,
        )

        cls.post2 = Post.objects.create(
            title="other post",
            body="Content of other post",
            author=cls.user2,
        )

    def test_user_can_update_own_post(self):
        """User should be able to update their own post"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("posts-detail", kwargs={"pk": self.post1.id})
        data = {
            "title": "Update by owner",
            "body": "Update content",
            "author": self.user1.id
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the change
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.title, "Update by owner")

    def test_user_cannot_update_other_post(self):
        """User should not be able to update other user's post"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("posts-detail", kwargs={"pk": self.post2.id})
        data = {
            "title": "Hacked post",
            "body": "Hacked content",
            "author": self.user1.id
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_other_post(self):
        """User should not be able to delete other user's post"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("posts-detail", kwargs={"pk": self.post2.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        cls.regular_user = get_user_model().objects.create_user(
            username='regular',
            password='regularpass',
            is_staff=False
        )

    def test_list_users_admin(self):
        """Test that admin users can list users"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("users-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_regular(self):
        """Test that regular users cannot list users"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse("users-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_users_unauthenticated(self):
        """Test that unauthenticated users cannot list users"""
        response = self.client.get(reverse("users-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)