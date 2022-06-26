from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
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
            text='Т'*20,
            author=cls.user,
            group=cls.group,
        )

    def test_post_str_max_length_not_exceed(self):
        post = Post.objects.first()
        self.assertEqual(str(post), self.post.text[:15])

    def test_group_slug(self):
        group = Group.objects.first()
        self.assertEqual(str(group.title), self.group.title)

    def test_help_text_post(self):
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_post(self):
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор публикации',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field
                    ).verbose_name, expected_value)
