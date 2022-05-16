from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.not_author = User.objects.create_user(username='mju')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug-group',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Т'*20,
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.not_author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client.force_login(self.not_author)
        self.templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.author.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
            'posts/create_post.html': f'/posts/{self.post.id}/edit/',
            'posts/create_post.html': '/create/',
        }

    def test_urls_uses_correct_template(self):
        for template, address in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
        response = self.not_author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, (f'/posts/{self.post.id}/')
        )
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )
