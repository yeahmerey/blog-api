from django.contrib import admin, messages
from django.db import models
from django.db.models import Count
from django.shortcuts import redirect
from unfold.decorators import action
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    RangeDateTimeFilter,
)
from django.urls import reverse
from django.utils.html import format_html
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import display
from unfold.sections import TableSection

from apps.blog.models import Post, Category, Tag, Comment


COMMENT_BODY_MAX_LENGTH = 50


class CategoryPostsSection(TableSection):
    verbose_name = "Posts in this category"
    related_name = "post_set"
    fields = [
        "title",
        "status",
        "created_at",
    ]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {
        "slug": ("name",),
    }
    list_sections = [CategoryPostsSection]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            posts_count=Count("post")
        ).prefetch_related("post_set")

    @display(
        description="Posts",
        ordering="posts_count",
    )
    def posts_count(self, obj):
        return obj.posts_count


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug", "posts_count")
    search_fields = ("name",)
    prepopulated_fields = {
        "slug": ("name",),
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            posts_count=Count("post", distinct=True)
        )

    @display(
        description="Posts",
        ordering="posts_count",
    )
    def posts_count(self, obj):
        return obj.posts_count


class CommentInline(TabularInline):
    model = Comment
    tab = True
    extra = 0
    per_page = 10

    fields = (
        "author",
        "body",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "author",
    )

    ordering = ("-created_at",)


@admin.register(Post)
class PostAdmin(ModelAdmin):
    inlines = [
        CommentInline,
    ]
    @action(
        description="Publish",
        url_path="publish",
        icon="publish",
    )
    
    def publish_post(self, request, object_id):
        post = Post.objects.get(pk=object_id)

        post.status = Post.Status.PUBLISHED
        post.save(update_fields=["status"])

        self.message_user(
            request,
            f"Post '{post.title}' published successfully.",
            messages.SUCCESS,
        )
    @action(
        description="Move to drafts",
        url_path="move-to-drafts",
        icon="unpublished",
    )
    def unpublish_post(self, request, object_id):
        post = Post.objects.get(pk=object_id)

        post.status = Post.Status.DRAFT
        post.save(update_fields=["status"])

        self.message_user(
            request,
            f"Post '{post.title}' moved to drafts.",
            messages.SUCCESS,
        )
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
    }

    fieldsets = (
        (
            "Content",
            {
                "classes": ["tab"],
                "fields": (
                    "title",
                    "slug",
                    "body",
                ),
            },
        ),
        (
            "Classification",
            {
                "classes": ["tab"],
                "fields": (
                    "category",
                    "tags",
                    "status",
                ),
            },
        ),
        (
            "Meta",
            {
                "classes": ["tab"],
                "fields": (
                    "author",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )


    actions_list = [
        "publish_all_drafts",
    ]

    @action(
        description="Publish all drafts",
        icon="publish",
    )
    def publish_all_drafts(self, request):
        updated = Post.objects.filter(
            status=Post.Status.DRAFT
        ).update(
            status=Post.Status.PUBLISHED
        )

        self.message_user(
            request,
            f"{updated} draft posts successfully published.",
            messages.SUCCESS,
        )

        return redirect("admin:blog_post_changelist")










    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @display(
        description="Status",
        label={
            "draft": "warning",
            "published": "success",
        },
    )
    def status_badge(self, obj):
        return obj.status

    list_display = (
        "title",
        "author",
        "category",
        "status_badge",
        "created_at",
        'comments_link'
    )
    actions_submit_line = [
        "save_and_publish",
    ]
    actions_submit_line = [
        "save_and_publish",
    ]
    warn_unsaved_form = True
    @action(
        description="Save & Publish",
        icon="publish",
    )
    def save_and_publish(self, request, obj):
        obj.status = Post.Status.PUBLISHED
        obj.save()
    @action(
        description="Save & Publish",
        icon="publish",
    )
    def save_and_publish(self, request, obj):
        obj.status = Post.Status.PUBLISHED
        obj.save()
        return obj
    search_fields = (
        "title",
        "body",
        "author__email",
    )

    list_filter = (
        "status",
        "category",
        "created_at",
    )

    ordering = ("-created_at",)
    list_per_page = 20

    autocomplete_fields = (
        "author",
        "category",
        "tags",
    )

    list_select_related = (
        "author",
        "category",
    )

    # Post Actions
    actions = (
        "publish_selected",
        "move_to_drafts",
    )

    @admin.action(description="Publish selected posts")
    def publish_selected(self, request, queryset):
        updated = queryset.update(
            status=Post.Status.PUBLISHED
        )

        self.message_user(
            request,
            f"{updated} posts successfully published.",
            messages.SUCCESS,
        )
    @display(description="Comments")
    def comments_link(self, obj):
        url = (
            reverse("admin:blog_comment_changelist")
            + f"?post__id__exact={obj.pk}"
        )

        return format_html(
            '<a href="{}">View comments ({})</a>',
            url,
            obj.comments.count(),
        )
    @admin.action(description="Move selected posts to drafts")
    def move_to_drafts(self, request, queryset):
        updated = queryset.update(
            status=Post.Status.DRAFT
        )

        self.message_user(
            request,
            f"{updated} posts moved to drafts.",
            messages.SUCCESS,
        )


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = (
        "post_title",
        "author",
        "short_body",
        "created_at",
    )

    list_filter = [
        ("post", AutocompleteSelectFilter),
        ("author", AutocompleteSelectFilter),
        ("created_at", RangeDateTimeFilter),
    ]

    list_filter_submit = True

    search_fields = (
        "body",
        "author__email",
        "post__title",
    )

    autocomplete_fields = (
        "post",
        "author",
    )

    list_select_related = (
        "post",
        "author",
    )

    @display(description="Post")
    def post_title(self, obj):
        return obj.post.title

    @display(description="Body")
    def short_body(self, obj):
        if len(obj.body) > COMMENT_BODY_MAX_LENGTH:
            return obj.body[:COMMENT_BODY_MAX_LENGTH] + "..."

        return obj.body
