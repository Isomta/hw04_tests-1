import shutil
import tempfile

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

    def func(self, request, bool=False):
        response = self.author_client.get(reverse(request))
        if bool:
            response.context['page_obj'].first()
        else:
            response.context['page_obj'].first()            

    def test_correct_context(self):
        response = self.author_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            INDEX_PAGE2_COUNT
        )

    def test_views_posts_correct_context(self):
        response = self.author_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            INDEX_PAGE2_COUNT
        )

    def test_views_group_correct_context(self):
        response = self.author_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            GROUP_PAGE2_COUNT
        )
        for item in range(len(response.context)):
            self.assertEqual(self.post.group, response.context[item]['group'])
        response = self.author_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.group.slug})
        )
        post_count = Post.objects.all().count()
        self.assertEqual(post_count, GROUP_COUNT + NO_GROUP_COUNT)
        group_count = Post.objects.filter(group_id=self.group.id).count()
        self.assertEqual(group_count, GROUP_COUNT)

    def test_views_profile_correct_context(self):
        another_author_post_count = Post.objects.filter(
            author=self.another_author.id
        ).count()
        self.assertEqual(another_author_post_count, NO_GROUP_COUNT)
        author_post_count = Post.objects.filter(author=self.author.id).count()
        self.assertEqual(author_post_count, GROUP_COUNT)
        response = self.author_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.author.username}) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj'].object_list),
            GROUP_PAGE2_COUNT
        )

    def test_views_post_detail_correct_context(self):
        response = self.author_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1})
        )
        self.assertEqual(response.context.get('post').text, POST_TEXT)

    def test_views_post_edit_form_correct_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        response = self.author_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': 1})
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_create_form_correct_context(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        response = self.author_client.get(reverse('posts:post_create'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_create(self):
        new_user = User.objects.create_user(username='new')
        group = Group.objects.create(
            title='Новая группа',
            slug='new_group',
            description='Описание новой группы',
        )
        post = Post.objects.create(
            text='New post',
            author=new_user,
            group=group,
            )
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][0].text, post.text)
        response = self.author_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': post.group.slug})
        )
        self.assertEqual(response.context['page_obj'][0].group, post.group)
        response = self.author_client.get(reverse(
            'posts:profile',
            kwargs={'username': new_user.username})
        )
        self.assertEqual(response.context['page_obj'][0].text, post.text)
        
        response = self.author_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': self.post.group.slug})
        )
        self.assertNotEqual(response.context['page_obj'][0].group, post.group)

    def test_post_has_image(self):
        test_jpg = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        name='test.jpg'
        uploaded = SimpleUploadedFile(
            name=name,
            content=test_jpg,
            content_type='image/jpg'
        )
        Post.objects.create(
                text=POST_TEXT,
                author=self.author,
                group=self.group,
                image = uploaded,
            )
        post = Post.objects.first()
        url_name = (
            ('posts:index', None),
            ('posts:profile', (self.author.username,)),
            ('posts:group_posts', (self.group.slug,)),
            ('posts:post_detail', (post.id,)),

        )
        for name, args in url_name:
            response = self.author_client.get(
                reverse(name, args=args)
            )
            if name == 'posts:post_detail':
                self.assertEqual(response.context.get('post').image.name, post.image.name)
            else:
                self.assertEqual(response.context['page_obj'][0].image.name, post.image.name)

    def test_comment_login_required(self):
        text = 'новый комментарий'
        comment = Comment.objects.create(
            post = self.post,
            author = self.author,
            text = text,
        )
        response = self.author_client.get(reverse('posts:post_detail', args=(self.post.id,)))
        self.assertEqual(response.context.get('post').comments.get(id=comment.id).text, text)
        response = self.client.get(reverse('posts:add_comment', args=(self.post.id,)))
        post_id = self.post.id
        url = reverse('users:login')
        url = f'{url}?next=/posts/{post_id}/comment/'
        self.assertRedirects(response, url)

class PostsTestsAnother(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.group = Group.objects.create(
            title='Название группы 1',
            slug='group1',
            description='Группа1',
        )
        for _ in range(GROUP_COUNT+NO_GROUP_COUNT):
            cls.post = Post.objects.create(
                text=POST_TEXT,
                author=cls.author,
            )

    def test_cache(self):
        post = Post.objects.create(
            text='8'*8,
            author=self.author,
        )
        response1 = self.client.get(reverse('posts:index'))
        post.delete()
        response2 = self.client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)

    def test_paginator(self):
        tuple = (('?page=1', 10), ('?page=2', 4))
        def func(self, page, count):
            response = self.client.get(reverse('posts:index') + page)
            page_post_count = len(response.context['page_obj'].object_list)
            self.assertEqual(page_post_count, count)
        for page, count in tuple:
            with self.subTest(page=page):
                func(self, page, count)

    def test_post_correct_group(self):
        response = self.client.get(reverse('posts:group_posts', args=(self.group.slug,)))
        count = response.context['page_obj'].paginator.count
        post = Post.objects.create(
            text='8'*8,
            author=self.author,
            group=self.group,
        )
        group = Group.objects.create(
            title='Название группы 2',
            slug='group2',
            description='Группа2',
        )
        response1 = self.client.get(reverse('posts:group_posts', args=(group.slug,)))
        count1 = response1.context['page_obj'].paginator.count
        response2 = self.client.get(reverse('posts:group_posts', args=(self.group.slug,)))
        count2 = response2.context['page_obj'].paginator.count
        self.assertEqual(count+1, count2)
        self.assertEqual(count1, 0)
