from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.not_author = User.objects.create_user(username='gav')
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
        self.author_client = Client()
        self.not_author_client = Client()
        self.author_client.force_login(self.author)
        self.not_author_client.force_login(self.not_author)
        self.templates_url_names = (
            (
                'posts/index.html',
                'posts:index', None, '/'
            ),
            (
                'posts/group_list.html',
                'posts:group_posts',
                (self.group.slug,),
                f'/group/{self.group.slug}/'
            ),
            (
                'posts/profile.html',
                'posts:profile',
                (self.author.username,),
                f'/profile/{self.post.author.username}/'
            ),
            (
                'posts/create_post.html',
                'posts:post_edit',
                (self.post.id,),
                f'/posts/{self.post.id}/edit/'
            ),
            (
                'posts/post_detail.html',
                'posts:post_detail',
                (self.post.id,),
                f'/posts/{self.post.id}/'
            ),
            (
                'posts/create_post.html',
                'posts:post_create',
                None,
                '/create/'
            ),
        )

    def func_assertEqualTemplateUsed(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.template)

    def test_url_author(self):
        for self.template, address, args, hard in self.templates_url_names:
            with self.subTest(address=address):
                response_name = self.author_client.get(
                    reverse(address, args=args)
                )

                self.func_assertEqualTemplateUsed(response_name)
                self.assertEqual(reverse(address, args=args), hard)

    def test_url_not_author(self):
        space_name = (
            'posts:post_edit',
        )
        for self.template, address, args, _ in self.templates_url_names:
            with self.subTest(address=address):
                response = self.not_author_client.get(
                    reverse(address, args=args)
                )
                if address in space_name:
                    self.assertRedirects(
                        response, reverse('posts:post_detail', args=args)
                    )
                else:
                    self.func_assertEqualTemplateUsed(response)

    def test_url_guest(self):
        space_name = (
            'posts:post_edit',
            'posts:post_create',
        )
        for self.template, address, args, _ in self.templates_url_names:
            with self.subTest(address=address):
                response = self.client.get(reverse(address, args=args))
                if address in space_name:
                    user_login = reverse('users:login')
                    action = reverse(address, args=args)
                    self.assertRedirects(
                        response, f'{user_login}?next={action}'
                    )
                else:
                    self.func_assertEqualTemplateUsed(response)
