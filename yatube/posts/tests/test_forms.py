import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

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
        test_jpg = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        name='test.jpg'
        cls.uploaded = SimpleUploadedFile(
            name=name,
            content=test_jpg,
            content_type='image/jpg'
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст',
            'image': self.uploaded,
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

    def test_create_comment(self):
            comments_count = Comment.objects.count()
            form_data = {
                'post': self.post,
                'author': self.user,
                'text': 'text',
            }
            response = self.author_client.post(
                reverse('posts:add_comment', args=(self.post.id,)),
                data=form_data,
                follow=True,
            )
            self.assertRedirects(
                response,
                reverse('posts:post_detail', args=(self.post.id,))
            )
            self.assertEqual(Comment.objects.count(), comments_count+1)

