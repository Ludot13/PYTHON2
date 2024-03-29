from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста',
                            help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    TEN_ACTS = 10
    FIRST_POST = 1
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(Group, blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Выберите группу')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField('Текст комментария',
                            help_text='Введите текст комментария')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост')
    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Последователь')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Последуемый')
