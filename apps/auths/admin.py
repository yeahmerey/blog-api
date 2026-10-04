from django.contrib.admin import register, ModelAdmin
from apps.auths.models import CustomUser

@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = (
        "id", 
        "email",
        "first_name",
        "last_name", 
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "is_staff",
    )