import shutil
import tempfile

from django import forms
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.utils import POSTS_PER_PAGE
from django.test import(
    TestCase,
    Client,
    override_settings
)
from posts.models import(
    Post,
    Group,
    Comment,
    Follow,
)
from posts.const import(
    INDEX_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_CREATE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    FOLLOW_INDEX_TEMPLATE,

    INDEX_URL_NAME,
    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
    POST_CREATE_URL_NAME,
    POST_EDIT_URL_NAME,
    GROUP_LIST_URL_NAME,
    USERS_LOGIN_URL_NAME,
    FOLLOW_INDEX_URL_NAME,
    PROFILE_FOLLOW_URL_NAME,
    PROFILE_UNFOLLOW_URL_NAME,
)


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# количество постов в тестовой БД для тестирования работы поджинатора
POSTS_IN_TEST_DB = POSTS_PER_PAGE + 3

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_auth')
        cls.user = User.objects.create_user(username='test_user')
        cls.user_follower = User.objects.create_user(username='user_follower')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.group_additional = Group.objects.create(
            title='Test group2',
            slug='test-slug2',
            description='Test description2'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Text test post more more more more text',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user_author,
            post=cls.post,
            text='Comment test text'
        )
        cls.index_url = reverse(INDEX_URL_NAME)
        cls.group_list_url = reverse(
            GROUP_LIST_URL_NAME, kwargs={'slug': cls.group.slug})
        cls.group_list_additional_url = reverse(
            GROUP_LIST_URL_NAME, kwargs={'slug': cls.group_additional.slug})
        cls.profile_url = reverse(
            PROFILE_URL_NAME, kwargs={'username': cls.user_author.username})
        cls.post_create_url = reverse(POST_CREATE_URL_NAME)
        cls.post_edit_url = reverse(
            POST_EDIT_URL_NAME, kwargs={'post_id': cls.post.id})
        cls.post_detail_url = reverse(
            POST_DETAIL_URL_NAME, kwargs={'post_id': cls.post.id})
        cls.login_url = reverse(USERS_LOGIN_URL_NAME)
        cls.follow_index_url = reverse(FOLLOW_INDEX_URL_NAME)
        cls.profile_follow_url = reverse(
            PROFILE_FOLLOW_URL_NAME,
            kwargs={'username': cls.user_author.username})
        cls.profile_unfollow_url = reverse(
            PROFILE_UNFOLLOW_URL_NAME,
            kwargs={'username': cls.user_author.username})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        cache.clear()

    def context_post_compare(self, context):
        """Сравнивает пост из контекста с постом, созданным в setUpClass"""
        attributes = [
            'text',
            'author',
            'pub_date',
            'group',
            'image'
        ]
        for attribute in attributes:
            self.assertEqual(
                getattr(context, attribute), getattr(self.post, attribute)
            )

    def test_pages_use_correct_template(self):
        """при обращении к namespace:name вызывается
        соответствующий HTML-шаблон
        """
        urls_templates = {
            self.index_url: INDEX_TEMPLATE,
            self.profile_url: PROFILE_TEMPLATE,
            self.post_detail_url: POST_DETAIL_TEMPLATE,
            self.post_create_url: POST_CREATE_TEMPLATE,
            self.post_edit_url: POST_CREATE_TEMPLATE,
            self.group_list_url: GROUP_LIST_TEMPLATE,
            self.follow_index_url: FOLLOW_INDEX_TEMPLATE,
        }
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_detail_check_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(
            self.post_detail_url
        )
        context = response.context.get('post')
        self.context_post_compare(context)
        self.assertEqual(
            response.context.get('posts_count'),
            self.post.author.posts.count())
        self.assertEqual(
            response.context.get('comments').first(),
            self.comment
        )

    def test_post_create_check_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(self.post_create_url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertFalse(response.context.get('is_edit'))

    def test_post_edit_check_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(
            self.post_edit_url)
        attributes = [
            'text',
            'group',
            'image'
        ]
        for attribute in attributes:
            self.assertEqual(
                getattr(response.context.get('form').instance, attribute), 
                getattr(self.post, attribute)
            )
        self.assertTrue(response.context.get('is_edit'))

    def test_templates_with_post_lists_check_context(self):
        """Шаблоны index, profile, group_list сформированы
        с правильным контекстом
        """
        templates_urls = [
            self.index_url,
            self.profile_url,
            self.group_list_url
        ]
        for url in templates_urls:
            response = self.authorized_client_author.get(url)
            first_post = response.context['page_obj'][0]
            self.context_post_compare(first_post)

    def test_additional_group_list_context(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен
        """
        response = self.authorized_client_author.get(
            self.group_list_additional_url)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_cache(self):
        """Проверка кэширования главной страницы"""
        post = Post.objects.create(
            author=self.user_author,
            text='Test cache',
        )
        response_1 = self.authorized_client_author.get(self.index_url)
        post.delete()
        response_2 = self.authorized_client_author.get(self.index_url)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_client_author.get(self.index_url)
        self.assertNotEqual(response_1.content, response_3.content)

    def test_follow_unfollow(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.get(self.profile_follow_url)
        self.assertEqual(self.user, self.user_author.following.first().user)
        self.authorized_client.get(self.profile_unfollow_url)
        self.assertIsNone(self.user.follower.first())

    def test_follow_context(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.user_follower)
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_author
        )
        new_post = Post.objects.create(
            author=self.user_author,
            text='Test follower'
        )
        response_follower = self.follower_client.get(self.follow_index_url)
        posts_follower = response_follower.context['page_obj']
        self.assertIn(new_post, posts_follower)
        response_unfollower = self.unfollower_client.get(
            self.follow_index_url)
        posts_unfollower = response_unfollower.context['page_obj']
        self.assertNotIn(new_post, posts_unfollower)



class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        posts = list()
        for i in range(POSTS_IN_TEST_DB):
            posts.append(
                Post(
                    author=cls.user_author,
                    text=f'{i} Text test post more more more more text',
                    group=cls.group
                )
            )
        Post.objects.bulk_create(posts)
        cls.index_url = reverse(INDEX_URL_NAME)
        cls.group_list_url = reverse(
            GROUP_LIST_URL_NAME, kwargs={'slug': cls.group.slug})
        cls.profile_url = reverse(
            PROFILE_URL_NAME, kwargs={'username': cls.user_author.username})

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_first_page_contains_POSTS_PER_PAGE_records(self):
        """Проверка: на первой странице должно быть POSTS_PER_PAGE постов"""
        templates_urls = [
            self.index_url,
            self.profile_url,
            self.group_list_url
        ]
        for url in templates_urls:
            response = self.guest_client.get(url)
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста"""
        templates_urls = [
            self.index_url,
            self.profile_url,
            self.group_list_url
        ]
        for url in templates_urls:
            response = self.guest_client.get(url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
