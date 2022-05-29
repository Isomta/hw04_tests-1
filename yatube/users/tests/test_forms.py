from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from users.forms import CreationForm

User = get_user_model()


class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='shav',
            email='123@qqq.ru',
        )

    def setUp(self):
        self.guest_client = Client()
        form = CreationForm()
        self.user_count = User.objects.count()

    def test_create_user_existing(self):
        form = {
            'first_name': 'Alex',
            'last_name': 'Shav',
            'username': 'mav',
            'password1': 'aPrCqVT5',
            'password2': 'aPrCqVT5',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form,
            follow=True
        )
        self.assertEqual(User.objects.count(), self.user_count+1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
