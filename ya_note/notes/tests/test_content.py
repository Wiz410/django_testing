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

    def test_object(self):
        """Тест объектов на странице."""
        user_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            obj_list = response.context['object_list']
            if status is True:
                self.assertIn(
                    self.note,
                    obj_list,
                    msg='На странице списка заметок нет заметок автора'
                )
            else:
                self.assertNotIn(
                    self.note,
                    obj_list,
                    msg='На странице списка заметок есть чужие заметки'
                )

    def test_form(self):
        """Тест формы на странице."""
        path_urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
        )
        for path, kwargs in path_urls:
            self.client.force_login(self.author)
            url = reverse(path, kwargs=kwargs)
            response = self.client.get(url)
            self.assertIn(
                'form',
                response.context,
                msg=f'На странице по адресу"{url}" нет формы заметки'
            )
