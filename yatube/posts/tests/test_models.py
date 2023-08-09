from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MAGICNUMBER = 15
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Ну очень длинный текст, чтобы прям вот ваааааааще',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        group = PostModelTest.group
        expected_post_str = post.text[:self.MAGICNUMBER]
        self.assertEqual(expected_post_str, str(post))
        expected_group_str = group.title
        self.assertEqual(expected_group_str, str(group))
