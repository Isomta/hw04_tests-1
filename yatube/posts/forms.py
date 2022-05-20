from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Текст нового поста',
        }
