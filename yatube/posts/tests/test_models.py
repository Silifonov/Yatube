from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Group, POST_NAME_LETTERS_COUNT

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text test post more more more more text'
        )

    def test_models_have_correct_objects_names(self):
        """Имена объектов (метод __str__) совпадают с ожидаемыми"""
        model_expected_name = {
            PostModelTest.post: PostModelTest.post.text[
                :POST_NAME_LETTERS_COUNT],
            PostModelTest.group: PostModelTest.group.title
        }
        for obj, expected_name in model_expected_name.items():
            with self.subTest(obj=obj):
                self.assertEqual(expected_name, str(obj))

    def test_verbose_name(self):
        """verbose_name полей в модели Post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )
