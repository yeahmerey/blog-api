from typing import Any 

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError

from django.db.models import (
    EmailField, 
    CharField, 
    BooleanField, 
)

from apps.abstracts.models import AbstractBaseModel

class CustomUserManager(BaseUserManager): 
    """Custom User Manager to make database requests"""

    def __obtain_user_instance(
            self, 
            email: str, 
            first_name: str, 
            last_name: str,
            password: str, 
            **kwargs: dict[str, Any], 
    ) -> 'CustomUser': 
        """Get user instance:"""
        if not email:
            raise ValidationError("Email field is required", code="email_empty")
        if not first_name: 
            raise ValidationError("First name field is required", code="first_name_empty")
        if not last_name:
            raise ValidationError("Last name field is required", code="last_name_empty")

        new_user: 'CustomUser' = self.model(
            email = self.normalize_email(email), 
            first_name = first_name,
            last_name = last_name,
            password = password,
            **kwargs, 
        )
        return new_user 

    def create_user(
            self, 
            email: str, 
            first_name: str,
            last_name: str,
            password: str, 
            **kwargs: dict[str, Any],
    ) -> 'CustomUser':
        new_user : 'CustomUser' = self.__obtain_user_instance(
            email= email, 
            first_name= first_name,
            last_name= last_name,
            password= password, 
            **kwargs,
        )
        new_user.set_password(password)
        new_user.save(using= self._db)
        return new_user
    def create_superuser(
            self, 
            email: str, 
            first_name: str,
            last_name: str,
            password: str, 
            **kwargs: dict[str, Any],
    ) -> 'CustomUser':
        new_superuser : 'CustomUser' = self.__obtain_user_instance(
            email= email, 
            first_name= first_name,
            last_name= last_name,
            password= password, 
            **kwargs,
        )
        new_superuser.is_staff = True
        new_superuser.is_superuser = True
        new_superuser.set_password(password)
        new_superuser.save(using= self._db)
        return new_superuser

class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom User model extending AbstractBaseModel
    """
    EMAIL_MAX_LENGTH = 150
    FULL_NAME_MAX_LENGTH = 150
    PASSWORD_MAX_LENGTH = 254

    email = EmailField(
        max_length = EMAIL_MAX_LENGTH, 
        unique = True,
        db_index = True,  
    )
    first_name = CharField(
        max_length = FULL_NAME_MAX_LENGTH, 
    )
    last_name = CharField(
        max_length = FULL_NAME_MAX_LENGTH, 
    )
    is_staff = BooleanField(
        default = False,
    )
    is_active = BooleanField(
        default = True,
    )

    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'
    objects = CustomUserManager()
