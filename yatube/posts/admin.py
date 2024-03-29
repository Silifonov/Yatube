from django.contrib import admin
from .models import (
    Post,
    Group,
    Follow,
    Comment,
)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description'
    )


admin.site.register(Group, GroupAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


admin.site.register(Follow, FollowAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'text',
        'created',
    )


admin.site.register(Comment, CommentAdmin)
