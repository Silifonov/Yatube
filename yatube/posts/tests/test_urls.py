from http import HTTPStatus
from django.test import (
    TestCase,
    Client
)
from django.core.cache import cache
from django.contrib.auth import get_user_model
from posts.models import (
    Post,
    Group
)
from posts.const import (
    INDEX_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    FOLLOW_INDEX_TEMPLATE,
)


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_auth')
        cls.user_not_author = User.objects.create_user(
            username='test_not_auth')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Text test post more more more more text'
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.index_url = '/'
        cls.profile_url = f'/profile/{cls.user_author.username}/'
        cls.post_detail_url = f'/posts/{str(cls.post.id)}/'
        cls.post_create_url = '/create/'
        cls.post_edit_url = f'/posts/{str(cls.post.id)}/edit/'
        cls.group_list_url = f'/group/{cls.group.slug}/'
        cls.users_login_url = '/auth/login/'
        cls.post_comment_url = f'/posts/{str(cls.post.id)}/comment/'
        cls.follow_index_url = '/follow/'
        cls.profile_follow_url = f'/profile/{cls.user_author.username}/follow/'
        cls.profile_unfollow_url = f'/profile/{cls.user_author.username}/unfollow/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTests.user_author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(
            PostURLTests.user_not_author)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = {
            self.index_url: INDEX_TEMPLATE,
            self.profile_url: PROFILE_TEMPLATE,
            self.post_detail_url: POST_DETAIL_TEMPLATE,
            self.post_create_url: POST_CREATE_TEMPLATE,
            self.post_edit_url: POST_CREATE_TEMPLATE,
            self.group_list_url: GROUP_LIST_TEMPLATE,
            self.follow_index_url: FOLLOW_INDEX_TEMPLATE,
            '/unexisting_page/': 'core/404.html'
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_url_for_guest_client(self):
        """Страницы доступные любому пользователю."""
        urls_for_guest_client = [
            self.index_url,
            self.group_list_url,
            self.profile_url,
            self.post_detail_url,
        ]
        for url in urls_for_guest_client:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_authorized_client_author(self):
        """Страницы доступные авторизоавнному пользователю (автору поста)."""
        url_for_authorized_client_author = [
            self.index_url,
            self.group_list_url,
            self.profile_url,
            self.post_detail_url,
            self.post_create_url,
            self.post_edit_url,
            self.follow_index_url,
        ]
        for url in url_for_authorized_client_author:
            response = self.authorized_client_author.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_authorized_client_not_author(self):
        """Страница 'post_edit' перенаправляет авторизоавнного
        пользователя (не автора поста) на страницу 'post_detail'.
        """
        response = self.authorized_client_not_author.get(
            self.post_edit_url, follow=True)
        self.assertRedirects(response, self.post_detail_url)

    def test_redirect_guest_client(self):
        """Страницы 'post_edit', 'post_create'  перенаправляют
        неавторизоавнного пользователя на страницу 'login'.
        """
        url_for_redirect_guest_client = [
            self.post_create_url,
            self.post_edit_url,
            self.post_comment_url,
            self.follow_index_url,
            self.profile_follow_url,
            self.profile_unfollow_url,
        ]
        for url in url_for_redirect_guest_client:
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(
                response, (self.users_login_url + '?next=' + url))

    def test_follow_unfollow_redirect(self):
        """Страница 'follow' и 'unfollow' перенаправляют авторизоавнного
        пользователя на страницу 'profile'.
        """
        url_follow_unfollow_redirect = [
            self.profile_follow_url,
            self.profile_unfollow_url,
        ]
        for url in url_follow_unfollow_redirect:
            response = self.authorized_client_not_author.get(url, follow=True)
            self.assertRedirects(response, self.profile_url)
    
    def test_unexisting_page(self):
        """Страница с несуществующим адресом возвращает 404 (NOT_FOUND)"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
