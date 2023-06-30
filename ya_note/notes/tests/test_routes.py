from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый Автор')
        cls.reader = User.objects.create(username='Тестовый Читатель')
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
            slug='test_slug',
            author=cls.author
        )

    def test_page_available_for_anon(self):
        """
        Тест доступных страниц для анонима.
        Страницы должни быть доступны не авторизированному пользователю.
        """
        path_urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for urls in path_urls:
            with self.subTest(urls=urls):
                url = reverse(urls)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    msg=f'Страница по адресу "{url}" не доступна анониму'
                )

    def test_pages_available_for_user(self):
        """
        Тест доступных страниц для авторизованного пользователя.
        Страницы должны быть доступны авторизированному пользователю.
        """
        path_url = (
            ('notes:list'),
            ('notes:add'),
            ('notes:success'),
        )
        for urls in path_url:
            with self.subTest(urls=urls):
                url = reverse(urls)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    msg=(
                        f'Страница по адресу "{url}" не доступна '
                        f'авторизированному пользователю'
                    )
                )

    def test_redirect_page_for_anon(self):
        """
        Тест страниц редиректа анонима.
        Страницы должны перенаправлять не авторизованного пользователя
        на страницу авторизации.
        """
        login_url = reverse('users:login')

        path_urls = (
            ('notes:add', None),
            ('notes:detail', {'slug': self.note.slug}),
            ('notes:edit', {'slug': self.note.slug}),
            ('notes:delete', {'slug': self.note.slug}),
            ('notes:list', None),
            ('notes:success', None),
        )
        for urls, kwargs in path_urls:
            with self.subTest(urls=urls):
                url = reverse(urls, kwargs=kwargs)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redirect_url,
                    msg_prefix=(
                        f'Страница по адресу "{url}" должна отправалять '
                        f'анонима на страницу логина'
                    )
                )

    def test_page_note_for_different_user(self):
        """
        Тест страницы заметки для разных пользователей.
        Страницы должны быть доступны автору заметки
        и не доступны другому пользователю.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            path_urls = (
                ('notes:detail'),
                ('notes:edit'),
                ('notes:delete'),
            )
            for urls in path_urls:
                with self.subTest(user=user, urls=urls):
                    url = reverse(urls, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(
                        response.status_code,
                        status,
                        msg=(
                            f'Для автора заметки страница "{url}" '
                            f'должна быть доступна 200, '
                            f'а для другого пользователя нет 404. '
                            f'Пользователь: "{user}" '
                            f'получил код: "{response.status_code}"'
                        )
                    )
