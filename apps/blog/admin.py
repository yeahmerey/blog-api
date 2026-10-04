from django.contrib.admin import ModelAdmin, register

from apps.blog.models import (
    Post, 
    Comment, 
    Category,
    Tag, 
)
@register(Post)
class PostAdmin(ModelAdmin):
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
    """Admin class for Post model"""


@register(Comment)
class CommentAdmin(ModelAdmin):
    class Meta : 
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
    """Admin class for Comment model"""


@register(Category)
class CategoryAdmin(ModelAdmin):
    class Meta :
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    """Admin class for Category model"""


@register(Tag)
class TagAdmin(ModelAdmin):
    class Meta :
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
    """Admin class for Tag model"""