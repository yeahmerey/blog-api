import os
from settings.conf import * 
from django.urls import reverse_lazy

# ------------------------------------
# Path
#

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = 'settings.urls'
WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'
AUTH_USER_MODEL = 'auths.CustomUser'

#--------------------------------------
# Apps
#
DJANGO_AND_THIRD_PARTY_APPS = [
    'unfold', 
    'unfold.contrib.filters', 
    'unfold.contrib.forms', 
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
]

PROJECT_APPS = [
    "apps.blog.apps.BlogConfig",
    "apps.abstracts.apps.AbstractsConfig",
    "apps.auths.apps.AuthsConfig",
]

INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS

#--------------------------------------
# Middleware | Templates | Validators
#

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

UNFOLD = {
    "SITE_TITLE": "Blog API", 
    "SITE_HEADER": "Blog Administration", 
    "SITE_SUBHEADER": "Content Management System",
    "SITE_SYMBOL": "article", 

    "COLORS" : {
        "primary" : {
            "50" : "#eff6ff", 
            "100" : "#dbeafe", 
            "200" : "#bfdbfe", 
            "300" : "#93c5fd", 
            "400" : "#60a5fa", 
            "500" : "#3b82f6", 
            "600" : "#2563eb", 
            "700" : "#1d4ed8", 
            "800" : "#1e40af", 
            "900" : "#1e3a8a", 
            "950" : "#172554", 
        },
    },
    "COMMAND" : {
        "search_models" : True, 
    },
    "DASHBOARD_CALLBACK": "apps.blog.callbacks.dashboard_callback",
    "TABS": [
        {
            "models": ["blog.post"],
            "items": [
                {
                    "title": "All",
                    "link": "/admin/blog/post/",
                },
                {
                    "title": "Published",
                    "link": "/admin/blog/post/?status__exact=published",
                },
                {
                    "title": "Drafts",
                    "link": "/admin/blog/post/?status__exact=draft",
                },
            ],
        },
    ],
    "ENVIRONMENT" : "apps.blog.callbacks.environment_callback", 
    "SITE_DROPDOWN" : [
        {
            "icon" : "code", 
            "title" : "GitHub Repository", 
            "link" : "https://github.com/", 
        }, 
        {
            "icon" : "description", 
            "title" : "Unfold Documentation", 
            "link" : "https://unfoldadmin.com/docs/"
        }, 
    ], 
    "SIDEBAR" : {
        "show_search" : True, 
        "show_all_applications" : False, 

        "navigation" : [ 
            {
                "title" : "Overview", 
                "separator":True ,
                "items":  [
                    {
                        "title" : "Dashboard", 
                        "icon" : "dashboard", 
                        "link" : reverse_lazy("admin:index"), 
                    },
                ],
            },
            {
                "title" : "Content", 
                "separator" : True, 
                "items" : [
                    {
                        "title" : "Posts", 
                        "icon" : "article", 
                        "link" : reverse_lazy(
                            "admin:blog_post_changelist"
                        ),
                        "badge" : "apps.blog.callbacks.drafts_badge",
                    },
                    {
                        "title" : "Comments", 
                        "icon" : "comment", 
                        "link": reverse_lazy(
                            "admin:blog_comment_changelist"
                        ), 
                    }, 
                    {
                        "title" : "Categories", 
                        "icon" : "folder", 
                        "link" : reverse_lazy(
                            "admin:blog_category_changelist"
                        ),
                    }, 
                    {
                        "title" : "Tags", 
                        "icon": "sell", 
                        "link" : reverse_lazy(
                            "admin:blog_tag_changelist"
                        ),
                    },
                ], 
            },
            {
                "title" : "Users & Access", 
                "separator" : True, 
                "permission" : lambda request : request.user.is_superuser, 
                "items": [
                    {
                        "title": "Users", 
                        "icon" : "people", 
                        "link" : reverse_lazy(
                            "admin:auths_customuser_changelist"
                        ), 
                    }, 
                    {
                        "title" : "Groups", 
                        "icon" : "shield", 
                        "link" : reverse_lazy(
                            "admin:auth_group_changelist"
                        ), 
                    }, 
                ],
            },
        ], 
    }
}


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
#----------------------------------------
# Internationalization
#
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

#----------------------------------------
# Static | Media
#
STATIC_URL = 'static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
