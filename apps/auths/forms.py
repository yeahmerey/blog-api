from unfold.forms import (
    UserChangeForm, 
    UserCreationForm, 
)
from apps.auths.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email", 
            "first_name", 
            "last_name", 
        )
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"