from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreate(TestCase):
    TITLE = 'Тестовый заголовок'
    TEXT = 'Тестовый текст'
    SLUG = 'Test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='Тестовый Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.redirect_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.redirect_url_anon = f'{cls.login_url}?next={cls.add_url}'
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }
        cls.form_data_no_slug = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': '',
        }

    def test_new_note_for_anon(self):
        """
        Тест создание заметки анонимом.
        Не авторизованный пользователь не должен
        иметь возможности создать заметку.
        """
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url_anon)
        note_count = Note.objects.count()
        self.assertEqual(
            note_count,
            0,
            msg='Аноним может создать заметку'
        )

    def test_new_note_for_user(self):
        """
        Тест создание заметки пользователем.
        Авторизованный пользователь должен
        иметь возможность создать заметку.
        """
        MSG_TEXT = (
            'Поле заметки сохраняется не правильно'
        )
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            1,
            msg='Пользователь не может создать заметку'
        )
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE, msg=MSG_TEXT)
        self.assertEqual(note.text, self.TEXT, msg=MSG_TEXT)
        self.assertEqual(note.slug, self.SLUG, msg=MSG_TEXT)
        self.assertEqual(note.author, self.author, msg=MSG_TEXT)

    def test_note_no_slug(self):
        """
        Тест автоматического создание slug.
        При не заполненном поле slug оно должно
        создасться автоматически из поля title.
        """
        response = self.author_client.post(
            self.add_url,
            data=self.form_data_no_slug
        )
        self.assertRedirects(response, self.redirect_url)
        note = Note.objects.get()
        self.assertEqual(
            note.slug,
            'testovyij-zagolovok',
            msg='Автоматическое поле slug создается не правильно'
        )


class TestEditDeleteNote(TestCase):
    TITLE = 'Тестовый заголовок'
    TEXT = 'Текст'
    SLUG = 'test_slug'
    NEW_TITLE = 'Тестовый заголовок изменен'
    NEW_TEXT = 'Текст изменен'
    NEW_SLUG = 'test_slug_new'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Тестовый Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.note_url = reverse(
            'notes:detail',
            kwargs={'slug': cls.note.slug}
        )
        cls.edit_note_url = reverse(
            'notes:edit',
            kwargs={'slug': cls.note.slug}
        )
        cls.delete_note_url = reverse(
            'notes:delete',
            kwargs={'slug': cls.note.slug}
        )
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }

    def test_edit_note_for_author(self):
        """
        Тест изменение заметок автором.
        Автор заметки должен иметь возможность изменить ее.
        """
        MSG_TEXT = (
            'Автор заметки не может ее редакитовать'
        )
        response = self.author_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE, msg=MSG_TEXT)
        self.assertEqual(self.note.text, self.NEW_TEXT, msg=MSG_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG, msg=MSG_TEXT)

    def test_edit_note_for_no_author(self):
        """
        Тест изменение заметок не автором.
        Только автор заметки должен иметь возможность изменить ее.
        """
        MSG_TEXT = (
            'Пользователь не должен иметь возможность '
            'редактировать чужие заметки'
        )
        response = self.reader_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title, msg=MSG_TEXT)
        self.assertEqual(self.note.text, note_from_db.text, msg=MSG_TEXT)
        self.assertEqual(self.note.slug, note_from_db.slug, msg=MSG_TEXT)

    def test_delete_note_for_author(self):
        """
        Тест удаления заметок автором.
        Автор заметки должен иметь возможность удалить ее.
        """
        response = self.author_client.delete(self.delete_note_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            0,
            msg=(
                'Автор заметки не может удалить ее'
            )
        )

    def test_delete_note_for_no_author(self):
        """
        Тест удаления заметок не автором.
        Только автор заметки должен иметь возможность удалить ее.
        """
        response = self.reader_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(
            notes_count,
            1,
            msg=(
                'Пользователь не должен иметь возможность '
                'удалять чужие заметки'
            )
        )


class TestNoteForm(TestCase):
    TITLE = 'Тестовый заголовок'
    TEXT = 'Текст'
    SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='Тестовый Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def test_unique_slug_error(self):
        """
        Тест ошибки уникального значения slug.
        Если поле slug не уникально
        форма должна вернуть ошибку.
        """
        response = self.author_client.post(
            self.add_url,
            data=self.form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING),
            msg_prefix=(
                'Если slug не уникален форма должна вернуть ошибку'
            )
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
