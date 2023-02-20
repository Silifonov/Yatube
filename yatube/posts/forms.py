from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {
            'text': {'required': 'Пост не может быть без текста'}
        }

        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)