import shutil
import tempfile
import datetime as dt

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

from yatube.settings import CUT_LENGTH as CL

User = get_user_model()

POST_TEXT = '0'*20
POST_TEXT_NO_GROUP = 'Нет группы'
GROUP_COUNT = 11
CL = 10
NO_GROUP_COUNT = 3
INDEX_PAGE2_COUNT = GROUP_COUNT + NO_GROUP_COUNT - CL
GROUP_PAGE2_COUNT = GROUP_COUNT - CL
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.another_author = User.objects.create_user(username='sam')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug-group',
            description='Описание группы',
        )
        for _ in range(GROUP_COUNT):
            cls.post = Post.objects.create(
                text=POST_TEXT,
                author=cls.author,
                group=cls.group,
            )
        for _ in range(NO_GROUP_COUNT):
            cls.post_no_group = Post.objects.create(
                text=POST_TEXT_NO_GROUP,
                author=cls.another_author,
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


###
    def func(self, request, bool=False):
        response = self.author_client.get(request)
        if bool:
            post = response.context['post']
        else:
            post = response.context['page_obj'][0]
        test_post = Post.objects.get(id=post.id)
        self.assertEqual(post.id, test_post.id)
        self.assertEqual(post.text, test_post.text)
        self.assertEqual(post.group, test_post.group)
        self.assertEqual(post.author, test_post.author)
        self.assertEqual(post.pub_date, test_post.pub_date)

    def test_context(self):
        execute = (
            (None, 'posts:index', None),
            ((self.group.slug,), 'posts:group_posts', None),
            ((self.author.username,), 'posts:profile', None),
            ((Post.objects.first().id,), 'posts:post_detail', True),
        )
        [self.func(reverse(i[1], args=i[0]), i[2]) for i in execute]
