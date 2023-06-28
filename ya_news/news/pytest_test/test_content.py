from django.conf import settings
from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_paginate_home(client, much_news):
    """Тест пагинации для главной страницы."""
    url = reverse('news:home')
    response = client.get(url)
    obj_list = response.context['object_list']
    news_count = len(obj_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
        'Количестов новостей на главной странице должно быть не более 10'
    )


@pytest.mark.django_db
def test_sorte_news(client, much_news):
    """Тест соритровки новостей."""
    url = reverse('news:home')
    response = client.get(url)
    obj_list = response.context['object_list']
    all_dates = [news.date for news in obj_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, (
        'Новости не отвортрованя по дате'
    )


@pytest.mark.django_db
def test_sorte_comment_on_news(client, news, much_comment):
    """Тест сортировки комментариев."""
    url = reverse('news:detail', kwargs={'pk': news.id})
    response = client.get(url)
    assert 'news' in response.context, (
        'Новость не передана в шаблон по ключу news'
    )
    all_comment = news.comment_set.all()
    assert all_comment[0].created < all_comment[1].created, (
        'Коментарии не отсоретованы старые в начале новые в конце'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (pytest.lazy_fixture('client'), 'anon'),
        (pytest.lazy_fixture('user_client'), 'user'),
    ),
)
def test_form_on_news(parametrized_client, status, news):
    """Тест доступности формы с комментариями."""
    url = reverse('news:detail', kwargs={'pk': news.id})
    response = parametrized_client.get(url)
    if status == 'anon':
        assert 'form' not in response.context, (
            'На странице новости анониму доступна форма комментариев'
        )
    else:
        assert 'form' in response.context, (
            'На странице новости авторизованному пользователю '
            'не доступна форма комментариев'
        )
