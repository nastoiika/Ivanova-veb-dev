import pytest
from app import create_app
from flask import url_for
from bs4 import BeautifulSoup
from app.repositories.visit_log_repository import VisitLogRepository

@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_admin_access(client):
    # Логинимся как админ
    client.post('/auth/login', data={
        'username': 'nastoika', 
        'password': '790011'
    }, follow_redirects=True)

    # Админ видит страницу списка пользователей
    response = client.get('/', follow_redirects=True)
    user_page = response.data.decode('utf-8')
    assert response.status_code == 200
    assert 'Добавить пользователя' in user_page  # кнопка доступна
    assert 'Отчеты' in user_page 

    # Админ может открыть страницу создания пользователя
    response = client.get('/users/new')
    assert response.status_code == 200

    # Админ может редактировать другого пользователя (например, id=10)
    response = client.get('/users/10/edit')
    assert response.status_code == 200

    # Админ может удалить пользователя (POST-запрос)
    response = client.post('/users/137/delete', follow_redirects=True)
    assert response.status_code == 200
    assert "Учетная запись удалена" in response.data.decode('utf-8')

    # Админ может просматривать профиль любого пользователя
    response = client.get('/users/10')
    assert response.status_code == 200


def test_buttons_visibility(client):
    # Залогинимся как пользователь с ролью admin
    client.post('/auth/login', data={'username': 'nastoika', 'password': '790011'}, follow_redirects=True)
    response = client.get('/')
    page = response.data.decode('utf-8')

    # Для админа кнопки "View", "Edit", "Delete" должны быть видны для всех пользователей
    assert 'Добавить пользователя' in page
    assert 'Отчеты' in page
    assert 'View' in page
    assert 'Edit' in page
    assert 'Delete' in page

    # Выходим
    client.get('/auth/logout', follow_redirects=True)

    # Логинимся как обычный пользователь (id=168)
    client.post('/auth/login', data={'username': 'nastoika1', 'password': '790011'}, follow_redirects=True)
    response = client.get('/')
    page = response.data.decode('utf-8')
    soup = BeautifulSoup(page, 'html.parser')

    assert 'Добавить пользователя' not in page
    assert 'Отчеты' not in page
    assert 'View' in page
    assert 'Edit' in page
    assert 'Delete' in page

    # Блок другого пользователя с id=2
    other_user_block = soup.find(attrs={"data-user-id": "2"})
    assert other_user_block is None

# ------------------------------------------------------------

def test_visit_log_page_elements(client):
    client.post('/auth/login', data={'username': 'nastoika', 'password': '790011'}, follow_redirects=True)
    response = client.get('log/report')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Проверяем заголовок страницы
    assert '<h2>Журнал посещений</h2>' in html

    # Проверяем наличие кнопок отчётов
    assert 'Отчёт по страницам' in html
    assert 'Отчёт по пользователям' in html

    # Проверяем заголовки таблицы
    assert '<th>№</th>' in html
    assert '<th>Пользователь</th>' in html
    assert '<th>Страница</th>' in html
    assert '<th>Дата</th>' in html

    # Проверяем наличие хотя бы одной строки с логом (если данные есть)
    # Можно проверить, что tbody существует и содержит tr
    assert '<tbody>' in html
    assert '<tr>' in html

    # Проверяем, что есть пагинация (класс pagination)
    assert 'class="pagination"' in html

def test_report_users(client):
    client.post('/auth/login', data={'username': 'nastoika', 'password': '790011'}, follow_redirects=True)
    response = client.get('log/report/users')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Проверяем заголовок страницы
    assert '<h2>Отчёт по пользователям</h2>' in html

    # Проверяем заголовки таблицы
    assert '<th>№</th>' in html
    assert '<th>Пользователь</th>' in html
    assert '<th>Количество посещений</th>' in html

    # Проверяем наличие хотя бы одной строки с логом (если данные есть)
    # Можно проверить, что tbody существует и содержит tr
    assert '<tbody>' in html
    assert '<tr>' in html

    assert 'Экспорт в CSV' in html

def test_report_pages(client):
    client.post('/auth/login', data={'username': 'nastoika', 'password': '790011'}, follow_redirects=True)
    response = client.get('log/report/pages')
    assert response.status_code == 200
    html = response.data.decode('utf-8')

    # Проверяем заголовок страницы
    assert '<h2>Отчёт по страницам</h2>' in html

    # Проверяем заголовки таблицы
    assert '<th>№</th>' in html
    assert '<th>Страница</th>' in html
    assert '<th>Количество посещений</th>' in html

    # Проверяем наличие хотя бы одной строки с логом (если данные есть)
    # Можно проверить, что tbody существует и содержит tr
    assert '<tbody>' in html
    assert '<tr>' in html

    assert 'Экспорт в CSV' in html

def test_export_report_by_csv(client):
    client.post('/auth/login', data={'username': 'nastoika', 'password': '790011'}, follow_redirects=True)
    response = client.get('/log/report/pages/export')  # путь к твоему экспорту
    assert response.status_code == 200

    # Проверка, что файл передаётся как attachment
    content_disposition = response.headers.get('Content-Disposition')
    assert content_disposition is not None
    assert 'attachment' in content_disposition
    assert 'report_by_pages.csv' in content_disposition

    response = client.get('/log/report/users/export')
    assert response.status_code == 200
    content_disposition = response.headers.get('Content-Disposition')
    assert content_disposition is not None
    assert 'attachment' in content_disposition
    assert 'report_by_users.csv' in content_disposition