from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path, kwargs',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_for_anon_user(client, path, kwargs):
    """Тестирование страниц для анонима."""
    if kwargs is not None:
        url = reverse(path, kwargs={'pk': kwargs.id})
    else:
        url = reverse(path)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'Страница по адресу "{url}" не доступна анониму'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('admin_client'), 'admin'),
        (pytest.lazy_fixture('client'), 'anon'),
        (pytest.lazy_fixture('user_client'), 'user'),
    ),
)
@pytest.mark.parametrize(
    'path',
    ('news:edit', 'news:delete'),
)
def test_edit_delete_for_different_user(
    parametrized_client,
    status,
    comment,
    path,
):
    """Тестирование страниц редактирования и удаления комментариев."""
    login_url = reverse('users:login')
    url = reverse(path, kwargs={'pk': comment.pk})
    expected_url = f'{login_url}?next={url}'
    response = parametrized_client.get(url)
    if status == 'user':
        assert response.status_code == HTTPStatus.OK, (
            f'Страница по адресу "{url}" не достопна автору комментария'
        )
    elif status == 'admin':
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            f'Страница по адресу "{url}" должна возвращать ошибку 404 '
            f'пользователям не являющемся автором комментария'
        )
    else:
        assertRedirects(
            response,
            expected_url,
            msg_prefix=(
                f'Страница по адресу "{url}" не перенапровляет '
                f'анонима на страницу логина "{login_url}"'
            ),
        )
