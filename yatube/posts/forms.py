from django.contrib.auth import get_user_model
from django import forms

from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст рецепта',
            'group': 'Раздел',
        }

        def not_empty_field(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError(
                    'Поле не должно оставаться пустым!'
                )
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
