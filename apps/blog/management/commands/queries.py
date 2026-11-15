from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Count, Max, Min
from django.test.utils import CaptureQueriesContext

from apps.blog.models import Category, Post, Tag
from apps.blog.queries import QUERIES

User = get_user_model()

PREVIEW_LIMIT = 5
EXCLUDED_NUMBERS = {40, 41, 42, 43, 44}


def get_two_tag_slugs():
    post = (
        Post.objects.annotate(tag_count=Count("tags"))
        .filter(tag_count__gte=2)
        .prefetch_related("tags")
        .first()
    )

    if post:
        tags = list(post.tags.all())
        return {
            "first_slug": tags[0].slug,
            "second_slug": tags[1].slug,
        }

    return {"first_slug": "api", "second_slug": "orm"}


def get_category_and_tag():
    post = (
        Post.objects.filter(
            category__isnull=False,
            tags__isnull=False
        )
        .select_related("category")
        .prefetch_related("tags")
        .first()
    )

    if post:
        return {
            "category_slug": post.category.slug,
            "tag_slug": post.tags.first().slug,
        }

    return {"category_slug": "django", "tag_slug": "api"}


def get_two_categories():
    categories = list(Category.objects.order_by("name")[:2])

    if len(categories) < 2:
        return {
            "source_slug": "python",
            "target_slug": "django",
        }

    return {
        "source_slug": categories[0].slug,
        "target_slug": categories[1].slug,
    }


SAMPLE_ARGUMENTS = {
    4: lambda: {
        "slug": Post.objects.values_list("slug", flat=True).first()
    },
    7: lambda: {"page": 1},
    8: lambda: {
        "word": (Post.objects.values_list("title", flat=True).first() or "a").split()[0]
    },
    9: lambda: {
        "domain": User.objects.values_list("email", flat=True).first().split("@")[-1]
    },
    11: lambda: {
        "slugs": list(Category.objects.values_list("slug", flat=True)[:3])
    },
    12: lambda: {
        "year": Post.objects.first().created_at.year,
        "month": Post.objects.first().created_at.month,
    },
    13: lambda: {"days": 30},
    14: lambda: {
        "start": Post.objects.aggregate(value=Min("created_at"))["value"].date(),
        "end": Post.objects.aggregate(value=Max("created_at"))["value"].date(),
    },
    15: lambda: {
        "email": Post.objects.select_related("author").first().author.email
    },
    16: lambda: {
        "tag_slug": Tag.objects.values_list("slug", flat=True).first()
    },
    17: lambda: {
        "category_slug": Category.objects.values_list("slug", flat=True).first()
    },
    21: get_two_tag_slugs,
    22: lambda: {
        "text": (Post.objects.values_list("title", flat=True).first() or "a").split()[0]
    },
    34: lambda: {"min_posts": 1},
    37: lambda: {
        "text": User.objects.exclude(first_name="").values_list(
            "first_name", flat=True
        ).first() or "a"
    },
    40: lambda: {"name": "Homework 3 Test"},
    41: lambda: {"days": 365},
    42: get_category_and_tag,
    43: get_two_categories,
}


class Command(BaseCommand):
    help = "Run ORM queries and display their results and SQL counts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            help="Run only one query by its number."
        )
        parser.add_argument(
            "--sql",
            action="store_true",
            help="Display SQL statements."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        number = options.get("number")
        show_sql = options.get("sql")

        if number is not None:
            if number not in QUERIES:
                raise CommandError(f"Query number {number} does not exist.")

            self.run_query(number, show_sql)
            return

        for query_number in QUERIES:
            if query_number in EXCLUDED_NUMBERS:
                continue

            self.run_query(query_number, show_sql)

    def run_query(self, number: int, show_sql: bool) -> None:
        function = QUERIES[number]
        arguments = SAMPLE_ARGUMENTS[number]() if number in SAMPLE_ARGUMENTS else {}

        with CaptureQueriesContext(connection) as context:
            result = function(**arguments)

            annotations = {}

            if hasattr(result, "query"):
                annotations = result.query.annotations
                rows = list(result)
            else:
                rows = result

        query_count = len(context.captured_queries)

        self.stdout.write(
            f"\n#{number} {function.__name__} — "
            f"{query_count} SQL queries"
        )

        if show_sql:
            for query in context.captured_queries:
                self.stdout.write(query["sql"])

        if hasattr(result, "query"):
            for obj in rows[:PREVIEW_LIMIT]:
                extra = {
                    name: getattr(obj, name)
                    for name in annotations
                }

                if extra:
                    self.stdout.write(f"  {obj} {extra}")
                else:
                    self.stdout.write(f"  {obj}")

            self.stdout.write(f"  ({len(rows)} rows)")

        elif isinstance(rows, list):
            for item in rows[:PREVIEW_LIMIT]:
                self.stdout.write(f"  {item}")

            self.stdout.write(f"  ({len(rows)} rows)")

        elif isinstance(rows, dict):
            if rows and all(isinstance(value, list) for value in rows.values()):
                items = list(rows.items())

                for item in items[:PREVIEW_LIMIT]:
                    self.stdout.write(f"  {item}")

                self.stdout.write(f"  ({len(items)} rows)")
            else:
                self.stdout.write(f"  {rows}")

        else:
            self.stdout.write(f"  {rows}")