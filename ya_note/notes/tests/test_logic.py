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

    def test_anon_new_note(self):
        """Тест создание заметки аноном."""
        self.client.post(self.add_url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_author_new_note(self):
        """Тест создание заметки автором."""
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.author)

    def test_note_no_slug(self):
        """Тест автомотического создание slug."""
        response = self.author_client.post(
            self.add_url,
            data=self.form_data_no_slug
        )
        self.assertRedirects(response, self.redirect_url)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, 'testovyij-zagolovok')
        self.assertEqual(note.author, self.author)


class TestEditDeleteNote(TestCase):
    TITLE = 'Тестовый заголовок'
    TEXT = 'Текст'
    SLUG = 'test_slug'
    NEW_TITLE = 'Тестовый заголовок изменет'
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

    def test_author_edit_note(self):
        """Тест изменение заметок автором."""
        response = self.author_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

    def test_user_edit_note(self):
        """Тест изменение заметок пользователем."""
        response = self.reader_client.post(
            self.edit_note_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_delete_note(self):
        """Тест удаление заметок автором."""
        response = self.author_client.delete(self.delete_note_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_delete_note(self):
        """Тест удаление заметок пользователем."""
        response = self.reader_client.delete(self.delete_note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


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
        """Тест ошибки уникального значения slug"""
        response = self.author_client.post(
            self.add_url,
            data=self.form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
