import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Post, Group, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='standartuser')
        cls.group = Group.objects.create(
            title='Test title longgggg',
            slug='test-slug',
            description='Test-description',
        )
        Post.objects.create(
            author=cls.user,
            text='Test text long very long',
            group=cls.group,
        )
        cls.group2 = Group.objects.create(
            title='Group number two',
            slug='slug-two',
            description='desc umber two'
        )
        cls.righter = User.objects.create_user(username='righter')
        cls.authorized_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client.force_login(self.righter)
        cache.clear()

    def test_create_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        post_data = {
            'text': 'Test title123',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=post_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.righter}
        ))
        lastpost = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(lastpost.text, post_data['text'])
        self.assertEqual(lastpost.author, self.righter)
        self.assertEqual(lastpost.group, self.group)
        self.assertTrue(
            Post.objects.filter(
                image='posts/small.gif'
            ).exists()
        )

    def test_update_post(self):
        smalling_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x01\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        smallest_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded3 = SimpleUploadedFile(
            name='smalling.gif',
            content=smalling_gif,
            content_type='image/gif'
        )
        uploaded4 = SimpleUploadedFile(
            name='smallest.gif',
            content=smallest_gif,
            content_type='image/gif',
        )

        Post.objects.create(
            author=self.righter,
            text='change_me',
            group=self.group,
            image=uploaded3,
        )
        posts_count = Post.objects.count()
        post_data = {
            'text': 'I changed you',
            'group': self.group2.id,
            'image': uploaded4,
        }
        response = self.authorized_client.post(
            reverse('posts:update_post', kwargs={'post_id': 2}),
            data=post_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 2}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_data['text'], Post.objects.get(pk=2).text)
        self.assertEqual(post_data['group'], Group.objects.get(pk=2).id)
        self.assertEqual('posts/smallest.gif', Post.objects.get(pk=2).image)

    def test_comment_under_post(self):
        comment_count = Comment.objects.count()
        Comment.objects.create(
            author=self.righter,
            text='Текст комментария длинный очень',
            post=Post.objects.get(pk=1)
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)


class PostCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="author")
        cls.post = Post.objects.create(
            text='another one strange text',
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_posts_cache(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        PostCacheTests.post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn(PostCacheTests.post.text, str(response.content))
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotIn(PostCacheTests.post.text, str(response.content))
