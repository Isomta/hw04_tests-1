from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='shav')
        cls.not_author = User.objects.create_user(username='mju')
        cls.group = Group.objects.create(
            title = 'Название группы',
            slug = 'slug-group',
            description = 'Описание группы',
        )
        cls.post = Post.objects.create(
            text='Т'*20,
            author = cls.author,
            group = cls.group,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.templates_url_hard = {
            '/password_change/done/': 'users/password_change_done.html',
            '/password_change/': 'users/password_change_form.html',
            '/logout/': 'users/logged_out.html',
            '/signup/':  'users/signup.html',
            '/login/': 'users/login.html',
            '/reset/done/': 'users/password_reset_complete.html',
            '/reset/<uidb64>/<token>/': 'users/password_reset_confirm.html',
            '/password_reset/done/': 'users/password_reset_done.html',
            '/password_reset/': 'users/password_reset_form.html',
        }
        self.templates_url_name = {
            'users/signup.html': 'users:signup',
            'users/login.html': 'users:login',
            'users/password_change_done.html': 'users:password_change_done',
            'users/password_change_form.html': 'users:password_change',
            'users/password_reset_complete.html': 'users:password_reset_complete',
            'users/password_reset_done.html': 'users:password_reset_done',
            'users/password_reset_form.html': 'users:password_reset',
            'users/logged_out.html': 'users:logout',
        }
 
    def test_urls_uses_correct_template(self):
        for address, template in self.templates_url_hard.items():
            with self.subTest(address=address):
                response = self.author_client.get(f'/auth{address}')
                self.assertTemplateUsed(response, template)

    def test_about_url_correct_template(self):
        response = self.author_client.get(reverse('users:signup')) 
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_urls_uses_correct_template(self):
        for template, name in self.templates_url_name.items():
            with self.subTest(address=name):
                response = self.author_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

    def test_password_reset_confirm_url_correct_template(self):
        response = self.author_client.get(reverse('users:password_reset_confirm', kwargs={'uidb64': '123', 'token': '123'})) 
        self.assertTemplateUsed(response, 'users/password_reset_confirm.html')

    def test_views_post_create_form_correct_context(self):
        form_fields = {
            'first_name': forms.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.CharField,
            'password2': forms.fields.CharField,
        }
        response = self.author_client.get(reverse('users:signup'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
