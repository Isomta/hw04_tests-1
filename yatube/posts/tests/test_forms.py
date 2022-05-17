from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='shav',
            email='123@qqq.ru',
        )
        cls.group = Group.objects.create(
            title='Название группы',
            slug='groupname',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.posts_count = Post.objects.count()

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), self.posts_count+1)

    def test_post_edit(self):
        form_data = {
            'text': 'Тестовый текст1',
            'group': self.group.id,
        }
        self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(
            text=form_data['text'],
            group=form_data['group']
        )
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.title, self.group.title)
