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
def test_page_available_for_anon(
    client,
    path,
    kwargs,
):
    """
    Тест доступных страниц для анонима.
    Страницы должны быть доступны не авторизированному пользователю.
    """
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
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('user_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'path',
    ('news:edit', 'news:delete'),
)
def test_edit_delete_comment_for_different_user(
    parametrized_client,
    status,
    comment,
    path,
):
    """
    Тест страницы редактирования и удаления комментариев для пользователей.
    Страницы должны быть доступны автору комментария
    и не доступны другому пользователю.
    """
    url = reverse(path, kwargs={'pk': comment.pk})
    response = parametrized_client.get(url)
    assert response.status_code == status, (
        f'Пользователь должен получить код "{status}" '
        f'а получил "{response.status_code}"'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path',
    ('news:edit', 'news:delete'),
)
def test_redirect_edit_delete_comment_for_anon(
    client,
    comment,
    path,
):
    """
    Тест страницы редактирования и удаления комментариев для анонима.
    Страницы должны перенаправлять не авторизованного пользователя
    на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(path, kwargs={'pk': comment.pk})
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(
        response,
        expected_url,
        msg_prefix=(
            f'Страница по адресу "{url}" не перенаправляет '
            f'анонима на страницу логина "{login_url}"'
        ),
    )
