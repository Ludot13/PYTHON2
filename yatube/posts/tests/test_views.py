from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django import forms
from itertools import islice

from posts.models import Post, Group, Follow
from posts.forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='JustUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Test-description',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test for testing paginator or anythong else',
        )

    def setup(self):
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/create_post.html': reverse('posts:create_post'),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['title'],
                         'Последние обновления на сайте'
                         )

    def test_group_post_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}
        ))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(response.context['title'], 'Записи сообщества')

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'JustUser'}
        ))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(len(response.context['posts']), 1)
        self.assertEqual(len(response.context['post_f']), 1)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(response.context['post'], self.post)

    def test_post_create_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertNotIn('is_edit', response.context)

    def test_post_edit_show_correct_context(self):
        Post.objects.create(
            author=self.user,
            text='text',
            group=self.group,
        )
        response = self.authorized_client.get(reverse(
            'posts:update_post', kwargs={'post_id': self.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context['is_edit'], True)

    def test_follow_index(self):
        Follow.objects.create(
            author=self.post.author,
            user=self.user
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        unuser = User.objects.create_user(username='unfollowed')
        authorized_unuser = Client()
        authorized_unuser.force_login(unuser)
        response = authorized_unuser.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_paginator(self):
        objs = (Post(author=self.user, group=self.group,
                text='post %s' % i) for i in range(13)
                )
        batch = list(islice(objs, 13))
        Post.objects.bulk_create(batch, 13)
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'JustUser'}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 4)
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)


class AdditionalTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_post_create_in_group(self):
        self.user = User.objects.create_user(username='JustUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='testdesc',
        )
        Group.objects.create(
            title='пустая группа',
            slug='empty-group',
            description='0 постов',
        )
        Post.objects.create(
            text='text1',
            group=group,
            author=self.user,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'empty-group'}
        ))
        self.assertEqual(len(response.context['page_obj']), 0)
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'JustUser'}),
        ]
        for url in url_list:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 1)

        Post.objects.create(
            author=self.user,
            group=group,
            text='text2',
        )
        for url in url_list:
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 2)
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'empty-group'}
        ))
        self.assertEqual(len(response.context['page_obj']), 0)
