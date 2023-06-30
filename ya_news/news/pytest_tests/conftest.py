from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import pytest

from news.models import News, Comment


@pytest.fixture
def user(django_user_model):
    """Фикстура пользователя."""
    return django_user_model.objects.create(username='Пользователь')


@pytest.fixture
def user_client(user, client):
    """Фикстура логина пользователя."""
    client.force_login(user)
    return client


@pytest.fixture
def news():
    """Фикстура новости."""
    news = News.objects.create(
        title='Новость',
        text='Текст новости.',
    )
    return news


@pytest.fixture
def much_news():
    """Фикстура с несколькими новостями."""
    today = datetime.today()
    news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news


@pytest.fixture
def comment(user, news):
    """Фикстура комментария к новости."""
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Комментарий к новости'
    )
    return comment


@pytest.fixture
def much_comment(user, news):
    """Фикстура комментарий к новости."""
    for index in range(2):
        now = timezone.now()
        comment = Comment.objects.create(
            news=news,
            author=user,
            text=f'Комментарий к новости {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return comment


@pytest.fixture
def form_data_comment():
    """Фикстура формы комментария."""
    return {
        'text': 'Новый комментарий к новости',
    }


@pytest.fixture
def url_for_news(news):
    """Фикстура ссылки на новость."""
    return reverse('news:detail', kwargs={'pk': news.id})
