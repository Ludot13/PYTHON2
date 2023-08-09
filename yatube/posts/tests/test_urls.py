import datetime
from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group, Follow

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='notauthor')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='AlmostGod'),
            pub_date=datetime.datetime.now(),
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Test-description'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        cache.clear()

    def test_homepage(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/unexistingpage/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                error_name: str = f'Error: {address} expected {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_pages_for_all(self):
        urls = [
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.post.author}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                error_name: str = f'Error with {url}'
                self.assertEqual(
                    response.status_code, HTTPStatus.OK, error_name
                )

    def test_edit_only_author(self):
        response = self.authorized_author.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_only_authorized(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page(self):
        response = self.guest_client.get('/IamErrorPage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_comment_only_auth(self):
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/comment/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get('/comment/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_follow_and_unfollow(self):
        follow_authors_count = Follow.objects.count()
        response = self.guest_client.get(
            f'/profile/{self.post.author}/follow/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_authors_count)
        response = self.authorized_client.get(
            f'/profile/{self.post.author}/follow/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_authors_count + 1)
        response = self.guest_client.get(
            f'/profile/{self.post.author}/unfollow/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_authors_count + 1)
        response = self.authorized_client.get(
            f'/profile/{self.post.author}/unfollow/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_authors_count)
