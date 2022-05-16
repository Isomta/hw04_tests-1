from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import CUT_LENGTH as CL

User = get_user_model()

POST_TEXT = '0'*20
POST_TEXT_NO_GROUP = 'Нет группы'
GROUP_COUNT = 11
CL = 10
NO_GROUP_COUNT = 3
INDEX_PAGE2_COUNT = GROUP_COUNT + NO_GROUP_COUNT - CL
GROUP_PAGE2_COUNT = GROUP_COUNT - CL


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

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }

    def test_views_posts_correct_template(self):
        for template, address in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
        response = self.author_client.get(reverse(
            'posts:post_delete',
            kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(
            response, (f'/profile/{self.author.username}/')
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
