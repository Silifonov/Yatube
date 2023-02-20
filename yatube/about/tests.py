from http import HTTPStatus
from django.urls import reverse
from django.test import (
    TestCase,
    Client
)

ABOUT_URL = '/about/author/'
TECH_URL = '/about/tech/'
ABOUT_URL_NAME = 'about:author'
TECH_URL_NAME = 'about:tech'
ABOUT_TEMPLATE = 'about/author.html'
TECH_TEMPLATE = 'about/tech.html'


class AboutURLTests(TestCase):
 
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = {
            ABOUT_URL: ABOUT_TEMPLATE,
            TECH_URL: TECH_TEMPLATE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = Client().get(url)
                self.assertTemplateUsed(response, template)

    def test_url_status(self):
        """Доступность статичных страниц."""
        urls = [
            ABOUT_URL,
            TECH_URL,
        ]
        for url in urls:
            response = Client().get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_template(self):
        """При обращении к namespace:name вызывается
        соответствующий HTML-шаблон.
        """
        about_url = reverse(ABOUT_URL_NAME)
        tech_url = reverse(TECH_URL_NAME)
        urls_templates = {
            about_url: ABOUT_TEMPLATE,
            tech_url: TECH_TEMPLATE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = Client().get(url)
                self.assertTemplateUsed(response, template)
