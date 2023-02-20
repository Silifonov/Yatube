import shutil
import tempfile

from django.urls import reverse
from posts.models import Post, Group
from django.test import Client, TestCase, override_settings
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POST_CREATE_URL_NAME = 'posts:post_create'
PROFILE_URL_NAME = 'posts:profile'
POST_DETAIL_URL_NAME = 'posts:post_detail'
POST_EDIT_URL_NAME = 'posts:post_edit'
USERS_LOGIN_URL_NAME = 'users:login'
POST_CREATE_URL = '/create/'
POST_COMMENT_URL_NAME = 'posts:add_comment'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='test_auth')
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.group_new = Group.objects.create(
            title='Test group new',
            slug='test-slug-new',
            description='Test description new'
        )
        cls.post_create_url = reverse(POST_CREATE_URL_NAME)
        cls.profile_url = reverse(
            PROFILE_URL_NAME, kwargs={'username': cls.user_author.username})
        cls.small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x80\x00\x00\x05\x04\x04'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x44'
            b'\x01\x00\x3b'
        )
        cls.uploaded_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=cls.small_gif_1,
            content_type='image/gif'
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=cls.small_gif_2,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)

    def test_create_post(self):
        """Cоздаётся новый пост в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': self.group.pk,
            'image': self.uploaded_1
        }
        response = self.authorized_client_author.post(
            self.post_create_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.profile_url)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image=f'posts/{self.uploaded_1.name}',
                author=self.user_author
            ).exists()
        )
        # Проверка редиректа неавторизованного пользователя
        self.guest_client = Client()
        response_guest = self.guest_client.post(
            self.post_create_url,
            data=form_data,
            follow=True
        )
        login_url = reverse(USERS_LOGIN_URL_NAME)
        self.assertRedirects(
            response_guest, (login_url + '?next=' + POST_CREATE_URL))

    def test_post_edit(self):
        """Происходит изменение созданного поста"""
        post = Post.objects.create(
            author=self.user_author,
            text='Test text',
            group=self.group,
            image=self.uploaded_1
        )
        post_count = Post.objects.count()
        post_edit_url = reverse(
            POST_EDIT_URL_NAME, kwargs={'post_id': post.id})
        post_detail_url = reverse(
            POST_DETAIL_URL_NAME, kwargs={'post_id': post.id})
        form_data = {
            'text': 'Test correct text',
            'group': self.group_new.pk,
            'image': self.uploaded_2
        }
        response = self.authorized_client_author.post(
            post_edit_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, post_detail_url)
        self.assertEqual(response.context.get('post').id, post.id)
        self.assertEqual(response.context.get('post').text, form_data['text'])
        self.assertEqual(
            response.context.get('post').group.pk, form_data['group'])
        self.assertEqual(
            response.context.get('post').author, self.user_author)
        self.assertEqual(
            response.context.get('post').image.name,
            f'posts/{self.uploaded_2.name}')
        self.assertEqual(Post.objects.count(), post_count)

    def test_add_comment(self):
        """Проверка формы комментария"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        post = Post.objects.create(
            author=self.user_author,
            text='Test text',
        )
        form_data = {'text': 'Test comment', }
        post_detail_url = reverse(
            POST_DETAIL_URL_NAME, kwargs={'post_id': post.id}
        )
        post_comment_url = reverse(
            POST_COMMENT_URL_NAME, kwargs={'post_id': post.id}
        )
        response = self.authorized_client.post(
            post_comment_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, post_detail_url)
        self.assertEqual(
            response.context.get('post').comments.first().text,
            form_data['text']
        )

        # Проверка редиректа неавторизованного пользователя
        self.guest_client = Client()
        response_guest = self.guest_client.post(
            post_comment_url,
            data=form_data,
            follow=True
        )
        login_url = reverse(USERS_LOGIN_URL_NAME)
        self.assertRedirects(
            response_guest, (login_url + '?next=' + post_comment_url))
