from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_user_create_comment(user_client, user, news, form_data_comment):
    """Тест создания комментария авторизированым пользователем."""
    url = reverse('news:detail', kwargs={'pk': news.id})
    redirect_url = f'{url}#comments'
    response = user_client.post(url, data=form_data_comment)
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1, (
        'Авторичированный пользователь не может '
        'оставить комментарий под новостью'
    )
    comment = Comment.objects.get()
    assert comment.text == 'Новый комментарий к новости', (
        'Текст комментария при сохранении отличается'
    )
    assert comment.author == user, (
        'Автор комментария при сохранении отличается'
    )
    assert comment.news == news, (
        'Новость для которой был комментария при сохранении отличается'
    )


@pytest.mark.django_db
def test_anon_no_create_comment(client, news, form_data_comment):
    """Тест создания комментария анонимом."""
    url = reverse('news:detail', kwargs={'pk': news.id})
    client.post(url, data=form_data_comment)
    assert Comment.objects.count() == 0, (
        'Аноним может оставить комментарий под новостью'
    )


@pytest.mark.django_db
def test_badwords_in_comment(user_client, news, form_data_comment):
    """Тест ошибки запрещеных слов."""
    url = reverse('news:detail', kwargs={'pk': news.id})
    form_data_comment['text'] = 'редиска выросла'
    response = user_client.post(url, data=form_data_comment)
    assertFormError(
        response,
        'form',
        'text',
        errors=(WARNING),
        msg_prefix=(
            'Проверка запрещенных слов не работает'
        )
    )


@pytest.mark.django_db
def test_author_edit_comment(user_client, news, comment, form_data_comment):
    """Тест редактирования комментария автором."""
    EDIT_TEXT = 'Измененный комментарий к новости'
    news_url = reverse('news:detail', kwargs={'pk': news.id})
    redirect_url = f'{news_url}#comments'
    url = reverse('news:edit', kwargs={'pk': comment.id})
    form_data_comment['text'] = EDIT_TEXT
    response = user_client.post(url, data=form_data_comment)
    assertRedirects(response, redirect_url)
    comment_get = Comment.objects.get(id=comment.id)
    assert comment_get.text == EDIT_TEXT, (
        'Автор комментария не может его редактировать'
    )


@pytest.mark.django_db
def test_no_author_edit_comment(
    admin_client,
    news,
    comment,
    form_data_comment
):
    """Тест редактирования комментария авторизованным пользователем."""
    EDIT_TEXT = 'Измененный комментарий к новости'
    url = reverse('news:edit', kwargs={'pk': comment.id})
    form_data_comment['text'] = EDIT_TEXT
    response = admin_client.post(url, data=form_data_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_get = Comment.objects.get(id=comment.id)
    assert comment_get.text == 'Комментарий к новости', (
        'Авторизованный пользователь может редактировать чужие комментарии'
    )


@pytest.mark.django_db
def test_author_delete_comment(user_client, news, comment):
    """Тест удаления комментария автором."""
    url = reverse('news:delete', kwargs={'pk': comment.id})
    news_url = reverse('news:detail', kwargs={'pk': news.id})
    redirect_url = f'{news_url}#comments'
    response = user_client.delete(url)
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0, (
        'Автор комментария не может его удалить'
    )


@pytest.mark.django_db
def test_no_author_delete_comment(admin_client, news, comment):
    """Тест удаления комментария авторизованным пользователем."""
    url = reverse('news:delete', kwargs={'pk': comment.id})
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1, (
        'Авторизованный пользователь может удалить чужой комментарий'
    )
