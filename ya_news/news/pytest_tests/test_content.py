from django.conf import settings
from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_paginate_for_home(
    client,
    much_news,
):
    """
    Тест пагинации для главной страницы.
    Список должен состоять из 10 новостей на страницу.
    """
    url = reverse('news:home')
    response = client.get(url)
    obj_list = response.context['object_list']
    news_count = len(obj_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'Колличество новостей на главной странице должно быть не более 10'
    )


@pytest.mark.django_db
def test_sorte_for_news(
    client,
    much_news,
):
    """
    Тест сортировки новостей.
    Новости должны быть отсортированы
    по дате от новых к старым.
    """
    url = reverse('news:home')
    response = client.get(url)
    obj_list = response.context['object_list']
    all_dates = [news.date for news in obj_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, (
        'Новости не отсортированы по дате'
    )


@pytest.mark.django_db
def test_sorte_for_comment_on_news(
    client,
    news,
    much_comment,
    url_for_news,
):
    """
    Тест сортировки комментариев.
    Коментарии должны быть отсортированы
    по дате от старых к новым.
    """
    response = client.get(url_for_news)
    assert 'news' in response.context, (
        'Новость не передана в шаблон по ключу news'
    )
    all_comment = news.comment_set.all()
    assert all_comment[0].created < all_comment[1].created, (
        'Коментарии не отсортированы старые в начале новые в конце'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), 'anon'),
        (pytest.lazy_fixture('user_client'), 'user'),
    ),
)
def test_form_for_comment_on_news(
    parametrized_client,
    status,
    news,
    url_for_news,
):
    """
    Тест доступности формы для отправки комментария.
    На странице новости должна быть доступна форма
    отправки комментариев для авторизированных пользователей.
    """
    response = parametrized_client.get(url_for_news)
    if status == 'anon':
        assert 'form' not in response.context, (
            'На странице новости анониму доступна форма комментариев'
        )
    else:
        assert 'form' in response.context, (
            'На странице новости авторизованному пользователю '
            'не доступна форма комментариев'
        )
