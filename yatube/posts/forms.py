from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Текст нового поста',
        }

class CommentForm(ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        labels = {
            # 'post': 'текст поста',
            # 'author': 'Автор комментария',
            'text': 'Текст комментария',
        }
        # help_texts = {
        #     'post': 'Текст поста',
        #     'author': 'Автор комментария',
        #     'text': 'Текст комментария',
        # }
