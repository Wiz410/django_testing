from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestFormObject(TestCase):

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

    def test_note_in_list_for_user(self):
        """
        Тест доступных заметок на странице.
        На странице заметка должна быть в списке
        И на странице списка заметок пользователю
        должны быть доступны только его заметки.
        """
        user_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in user_statuses:
            with self.subTest(user=user, status=status):
                self.client.force_login(user)
                url = reverse('notes:list')
                response = self.client.get(url)
                obj_list = response.context['object_list']
                if status is True:
                    self.assertIn(
                        self.note,
                        obj_list,
                        msg='На странице списка заметок нет заметок'
                    )
                else:
                    self.assertNotIn(
                        self.note,
                        obj_list,
                        msg='На странице списка заметок '
                            'доступны заметки других авторов'
                    )

    def test_form_on_page(self):
        """
        Тест доступности формы для отправки заметки.
        На страницах добавления и редактирования заметки
        должны быть доступны формы для отправки.
        """
        path_urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
        )
        for path, kwargs in path_urls:
            with self.subTest(path=path, kwargs=kwargs):
                self.client.force_login(self.author)
                url = reverse(path, kwargs=kwargs)
                response = self.client.get(url)
                self.assertIn(
                    'form',
                    response.context,
                    msg=f'На странице по адресу"{url}" '
                        f'форма заметки не доступна'
                )
