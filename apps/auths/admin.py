from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.forms import AdminPasswordChangeForm
from apps.auths.models import CustomUser

from apps.auths.forms import (
    CustomUserChangeForm, 
    CustomUserCreationForm, 
)
from apps.auths.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "user_header", 
        "active_status", 
        "staff_status", 
        "posts_count", 
    )

    search_fields = (
        "email", 
        "first_name", 
        "last_name", 
    )
    list_filter = (
        ("is_active", BooleanRadioFilter), 
        ("is_staff", BooleanRadioFilter),
    )

    ordering = ("email", )
    filter_horizontal = (
        "groups", 
        "user_permissions",
    )

    readonly_fields = (
        "last_login", 
    )
    add_fieldsets = (
        ( 
            "Create User", 
            {
                "classes" : ["wide"], 
                "fields": (
                    "email", 
                    "first_name", 
                    "last_name", 
                    "password1",
                    "password2",  
                ),
            },
        ),
    )

    actions = (
        "activate_users",
        "deactivate_users", 
    )
    fieldsets = (
        (
            "Personal Information", 
            {
                "classes": ["tab"],
                "fields": (
                    "email", 
                    "first_name", 
                    "last_name", 
                    "password", 
                ),
            },
        ),
        (
            "Permissions", 
            {
                "classes": ["tab"], 
                "fields" : (
                    "is_active", 
                    "is_staff", 
                    "is_superuser", 
                    "groups", 
                    "user_permissions",
                ),
            },
        ),
        (
            "Important Dates", 
            {
                "classes": ["tab"], 
                "fields": (
                    "last_login",
                ),
            },
        ),
    )
    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)

        self.message_user(
            request,
            f"{updated} users successfully activated.",
        )
    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)

        self.message_user(
            request,
            f"{updated} users successfully deactivated.",
        )
        
    def get_queryset(self, request): 
        queryset = super().get_queryset(request)

        return queryset.annotate(
            posts_count = Count("post")
        )
    @display(description="User", header=True)
    def user_header(self, obj):
        full_name = f"{obj.first_name}{obj.last_name}".strip()
        initials = (
            f"{obj.first_name[:1]}{obj.last_name[:1]}"
        ).upper()

        return [
            full_name or obj.email, 
            obj.email, 
            initials, 
        ]
    @display(
        description="Active",
        label={True:"success", False: "danger"},
    )
    def active_status(self , obj):
        return obj.is_active
    @display(
        description="Staff", 
        label={True:"info", False:"warning"},
    )
    def staff_status(self, obj):
        return obj.is_staff
    @display(
        description="Posts", 
        ordering="posts_count", 
    )
    def posts_count(self ,obj):
        return obj.posts_count



admin.site.unregister(Group)
admin.site.register(Group, ModelAdmin)

