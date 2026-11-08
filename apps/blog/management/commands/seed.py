from datetime import datetime
from random import choice, random, sample
from typing import Any 

from faker import Faker
from django.core.management.base import (
    BaseCommand,
    CommandError,
    CommandParser
)
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify
from apps.auths.models import CustomUser
from apps.blog.models import (
    Category,
    Post, 
    Comment,
    Tag,
)

class Command(BaseCommand):

    MAILBOX_DOMAINS = (
        "example.com", 
        "kbtu.kz"
    )

    DEFAULT_PASSWORD = "SeedPassword123!"
    SEED_PASSWORD = "SeedPassword123!"
    DEFAULT_USERS = 20 
    DEFAULT_POSTS = 100
    DEFAULT_COMMENTS = 500

    CATEGORY_NAMES = (
        "Python", 
        "Django", 
        "DevOps", 
        "JavaScript",
        "Database",
        "Docker", 
        "Git", 
        "Testing", 
    )

    TAG_NAMES = (
        "Backend", 
        "Frontend", 
        "API",
        "REST",
        "SQL", 
        "PostgreSQL",
        "Authentication",
        "Security",
        "Deployment",
        "Docker", 
        "GitHub",
        "Testing",
        "Python Basics", 
        "Web Development",
        "ORM", 
        "Performance",
        "Tutorials",
        "Programming",
        "FastAPI", 
        "JavaScript",
    )

    PUBLISHED_PERSENTAGE = 0.7
    CATEGORYLESS_PERSENTAGE = 0.1

    MIN_TAGS_PER_POST = 0
    MAX_TAGS_PER_POST = 5
    
    MIN_COMMENT_SENTENCES=1
    MAX_COMMENT_SENTENCES=3

    def __get_email_from_names(
            self, 
            first_name: str,
            last_name: str,
    ) -> str: 
        """
        Generate an email address based on the first and last name.
        """
        email_username: str = (
            f"{first_name}.{last_name}".lower()
        )
        return email_username + "@" + choice(self.MAILBOX_DOMAINS)

    #staff and inactive : 
    STAFF_USER_INTERVAL = 10
    INACTIVE_USER_INTERVAL = 5

    def __create_users(
            self,
            number_of_users: int, 
        ) -> int:
        """
        Create fake users
        """

        fake = Faker()
        users_to_create: list[CustomUser] = []

        existing_emails: set[str] = set(
            CustomUser.objects.values_list(
                "email", 
                flat=True
            ))
        hashed_password: str = make_password(self.SEED_PASSWORD)

        for i in range(number_of_users):
            first_name: str = fake.first_name()
            last_name: str = fake.last_name()
            email: str = self.__get_email_from_names(
                first_name=first_name, 
                last_name=last_name
            )

            # Ensure unique email addresses
            email_username , email_domain = email.split("@")

            suffix : int = 1

            while email in existing_emails:
                email = f"{email_username}{suffix}@{email_domain}"
                suffix += 1

            existing_emails.add(email)

            is_staff: bool = (
                (i+1) % self.STAFF_USER_INTERVAL == 0
            )

            is_active: bool = (
                (i+1) % self.INACTIVE_USER_INTERVAL != 0
            )

            users_to_create.append(
                CustomUser(
                    email = email, 
                    first_name = first_name,
                    last_name = last_name,
                    is_staff = is_staff,
                    is_active = is_active,
                    password = hashed_password
                )
            )
        CustomUser.objects.bulk_create(
            users_to_create,
            ignore_conflicts=True, 
            )
        self.stdout.write(
            f"Created {len(users_to_create)} users successfully."
        )
        return len(users_to_create)
    def __create_categories(self) -> int: 
        """
        Create blog categories. 
        """

        categories_to_create: list[Category] = []

        existing_names: set[str] = set(
            Category.objects.values_list(
                "name", 
                flat=True
            )
        )
        existing_slugs: set[str] = set(
            Category.objects.values_list(
                "slug", 
                flat=True
            )
        )

        for name in self.CATEGORY_NAMES:
            slug: str = slugify(name)

            if name in existing_names or slug in existing_slugs:
                continue

            categories_to_create.append(
                Category(
                    name = name, 
                    slug = slug
                )
            )

            existing_names.add(name)
            existing_slugs.add(slug)

        Category.objects.bulk_create(
            categories_to_create, 
        )
        self.stdout.write(
            f"Created {len(categories_to_create)} categories successfully."
        )
        return len(categories_to_create)

    MIN_POST_PARAGRAPHS = 2
    MAX_POST_PARAGRAPHS = 5

    MIN_SLUG_SUFFIX = 2

    def __create_posts(
            self, 
            number_of_posts: int,
    ) -> int: 
        """
        Create fake blog posts.
        """

        fake = Faker()
        users: list[CustomUser] = list(CustomUser.objects.all())
        categories: list[Category] = list(Category.objects.all())
        tags: list[Tag] = list(Tag.objects.all())

        posts_to_create: list[Post] = []

        existing_slugs: set[str] = set(
            Post.objects.values_list(
                "slug", 
                flat=True
            )
        )

        for _ in range(number_of_posts):
            author: CustomUser = choice(users)

            title: str = fake.sentence().rstrip(".")

            slug: str = slugify(title)

            base_slug: str = slug
            suffix: int = self.MIN_SLUG_SUFFIX

            while slug in existing_slugs:
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            existing_slugs.add(slug)

            body: str = "\n\n".join(
                fake.paragraphs(
                    nb = choice(
                        range(
                            self.MIN_POST_PARAGRAPHS,
                            self.MAX_POST_PARAGRAPHS + 1,
                        )
                    )
                )
            )

            if random() < self.CATEGORYLESS_PERSENTAGE:
                category: Category | None = None
            else:
                category: Category = choice(categories)

            if random() < self.PUBLISHED_PERSENTAGE:
                status: str = Post.Status.PUBLISHED
            else:
                status: str = Post.Status.DRAFT

            posts_to_create.append(
                Post(
                    author = author, 
                    title = title,
                    slug = slug,
                    body = body,
                    category = category,
                    status = status
                )
            )
        Post.objects.bulk_create(posts_to_create)
        for post in posts_to_create:
            post_tags: list[Tag] = sample(
                tags, 
                k=choice(
                    range(
                        self.MIN_TAGS_PER_POST, 
                        min(self.MAX_TAGS_PER_POST, len(tags)) + 1,                 
                    )
                ),
            )
            post.tags.set(post_tags)

        self.stdout.write(
            f"Created {len(posts_to_create)} posts successfully."
        )
        return len(posts_to_create)
       
    MIN_COMMENT_SENTENCES = 1
    MAX_COMMENT_SENTENCES = 3

    def __create_comments(
            self, 
            number_of_comments: int,
    ) -> int:
        """
        Create fake comments for blog posts.
        """

        fake = Faker()
        users: list[CustomUser] = list(CustomUser.objects.all())
        published_posts: list[Post] = list(
            Post.objects.filter(
                status = Post.Status.PUBLISHED
            )
        )
        comments_to_create: list[Comment] = []

        for _ in range(number_of_comments):
            post: Post = choice(published_posts)
            author: CustomUser = choice(users)
        
            sentence_count: int = choice(
                range(
                    self.MIN_COMMENT_SENTENCES, 
                    self.MAX_COMMENT_SENTENCES + 1
                )
            )
            body: str = " ".join(
                fake.sentences(
                    nb = sentence_count
                )
            )    
            comments_to_create.append(
                Comment(
                    post = post, 
                    author = author,
                    body = body
                )
            )
        Comment.objects.bulk_create(comments_to_create)
        self.stdout.write(
            f"Created {len(comments_to_create)} comments successfully."
        )
        return len(comments_to_create)

    help ="Fill the database with fake data for testing and development."

    def __create_tags(self) -> int:
        """
        Create blog tags.
        """

        tags_to_create: list[Tag] = []

        existing_names: set[str] = set(
            Tag.objects.values_list(
                "name", 
                flat=True
            )
        )
        existing_slugs: set[str] = set(
            Tag.objects.values_list(
                "slug", 
                flat=True
            )
        )
        for name in self.TAG_NAMES:
            slug : str = slugify(name)
            if name in existing_names or slug in existing_slugs:
                continue

            tags_to_create.append(
                Tag(
                    name = name,
                    slug = slug
                )
            )
            existing_names.add(name)
            existing_slugs.add(slug)
        Tag.objects.bulk_create(tags_to_create)
        self.stdout.write(
            f"Created {len(tags_to_create)} tags successfully."
        )
        return len(tags_to_create)
    
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--users", 
            type=int, 
            default=self.DEFAULT_USERS,
            help="Number of users to create.",
        )
        parser.add_argument(
            "--posts", 
            type=int, 
            default=self.DEFAULT_POSTS,
            help="Number of posts to create.",
        )
        parser.add_argument(
            "--comments", 
            type=int, 
            default=self.DEFAULT_COMMENTS,
            help="Number of comments to create.",
        )
        parser.add_argument(
            "--clear", 
            action = "store_true",
            help = "Delete existing data before seeding",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = datetime.now()

        users_count = options["users"]
        posts_count = options["posts"]
        comments_count = options["comments"]
        clear = options["clear"]

        #Validate input
        if min(users_count, posts_count, comments_count) < 0:
            raise CommandError(
                "Number of users, posts, and comments must be non-negative."
            )
        #Clear existing data if --clear option is provided
        if clear:
            self.__clear_data()

        #Create users
        created_users = self.__create_users(users_count)

        #Check if users exist
        if (posts_count > 0 or comments_count > 0) and not CustomUser.objects.exists():
            raise CommandError(
                "No users exist. Please create users first."
            )
        #create categories and tags
        created_categories = self.__create_categories()
        created_tags = self.__create_tags()

        #create posts 
        created_posts = self.__create_posts(posts_count)

        #Check published posts before creating comments
        if comments_count > 0 and not Post.objects.filter(
            status = Post.Status.PUBLISHED
        ).exists():
            raise CommandError(
                "Cannot create comments because there are no published posts. Please create published posts first." \
            )
        #create comments
        created_comments = self.__create_comments(comments_count)
        elapsed_time = (datetime.now() - start_time).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding completed successfully in {elapsed_time:.2f} seconds."
            )
        )
    def __clear_data(self) -> None:
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        CustomUser.objects.filter(is_superuser=False).delete()

        self.stdout.write(
            self.style.WARNING(
                "Existing data cleared successfully."
            )
        )
    