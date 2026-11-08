
import json
import os

from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.blog.models import Post, Comment, Category


User = get_user_model()


def environment_callback(request):
    environment = os.getenv("BLOG_ENV_ID", "local").lower()

    if environment == "production":
        return ["Production", "danger"]

    return ["Local", "warning"]


def drafts_badge(request):
    return Post.objects.filter(
        status=Post.Status.DRAFT
    ).count()


def dashboard_callback(request, context):
    # Statistics
    total_users = User.objects.count()

    published_posts = Post.objects.filter(
        status=Post.Status.PUBLISHED
    ).count()

    draft_posts = Post.objects.filter(
        status=Post.Status.DRAFT
    ).count()

    total_comments = Comment.objects.count()

    # Posts per category
    categories = Category.objects.annotate(
        posts_count=Count("post")
    ).order_by("-posts_count")

    chart_data = {
        "labels": [
            category.name for category in categories
        ],
        "datasets": [
            {
                "label": "Posts",
                "data": [
                    category.posts_count for category in categories
                ],
            }
        ],
    }

    # Top 5 authors
    top_authors = (
        User.objects.annotate(
            posts_count=Count("post")
        )
        .filter(posts_count__gt=0)
        .order_by("-posts_count")[:5]
    )

    # Published and draft percentages
    total_posts = published_posts + draft_posts

    published_percentage = (
        round(published_posts / total_posts * 100)
        if total_posts else 0
    )

    draft_percentage = (
        round(draft_posts / total_posts * 100)
        if total_posts else 0
    )

    context.update({
        "total_users": total_users,
        "published_posts": published_posts,
        "draft_posts": draft_posts,
        "total_comments": total_comments,
        "chart_data": json.dumps(chart_data),
        "top_authors": top_authors,
        "published_percentage": published_percentage,
        "draft_percentage": draft_percentage,
    })

    return context
