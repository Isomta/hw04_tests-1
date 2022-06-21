import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsTestsTemplate(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug-group',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Text post',
            author=cls.author,
            group=cls.group,
        )


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        
    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.templates_url_names = (
            ('posts/index.html', 'posts:index', None,),
            ('posts/group_list.html', 'posts:group_posts', (self.group.slug,)),
            ('posts/profile.html', 'posts:profile', (self.author.username,)),
            ('posts/create_post.html', 'posts:post_edit', (self.post.id,)),
            ('posts/post_detail.html', 'posts:post_detail', (self.post.id,)),
            ('posts/create_post.html', 'posts:post_create', None,),
        )

    def test_views_posts_correct_template(self):
        for template, address, args in self.templates_url_names:
            with self.subTest(address=address):
                response = self.author_client.get(reverse(address, args=args))
                self.assertTemplateUsed(response, template)
        response = self.author_client.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(
            response, (f'/profile/{self.author.username}/')
        )


class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug-group',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Text post',
            author=cls.author,
            group=cls.group,
        )

    def func(self, request, bool=False):
        response = self.client.get(request)
        if bool:
            post = response.context['post']
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pub_date, self.post.pub_date)

    def test_context(self):
        execute = (
            (None, 'posts:index', None),
            ((self.group.slug,), 'posts:group_posts', None),
            ((self.author.username,), 'posts:profile', None),
            ((Post.objects.first().id,), 'posts:post_detail', True),
        )
        [self.func(reverse(i[1], args=i[0]), i[2]) for i in execute]
