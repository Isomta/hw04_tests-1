import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
POST_COUNT = 12


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
        cls.user = User.objects.create_user(username='mav')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='slug-group',
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
        uploaded = SimpleUploadedFile(
            name='test.jpg',
            content=test_jpg,
            content_type='image/jpg'
        )
        for i in range(POST_COUNT):
            Post.objects.create(
                text=f'Text post {i}',
                author=cls.author,
                group=cls.group,
                image=uploaded,
            )
        cls.post = Post.objects.create(
            text='Text post',
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='comment text'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def func(self, request, bool=False):
        response = self.client.get(request)
        if bool:
            post = response.context['post']
        else:
            page_obj = response.context['page_obj']
            post = page_obj[0]
            self.assertEqual(len(page_obj.object_list), 10)
            self.assertEqual(
                len(
                    self.client.get(
                        request + '?page=2'
                    ).context['page_obj'].object_list
                ), 3)
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.comments.first(), self.comment)
        self.assertEqual(post.author.following.first(), self.follow)

    def test_context(self):
        execute = (
            (None, 'posts:index', None),
            ((self.group.slug,), 'posts:group_posts', None),
            ((self.author.username,), 'posts:profile', None),
            ((Post.objects.first().id,), 'posts:post_detail', True),
        )
        [self.func(reverse(i[1], args=i[0]), i[2]) for i in execute]
