from django.db import models

# Create your models here.
# django imports
from django.contrib.auth.models import Group
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

# local imports
from cinema_ebooking_system import constants


# Create your models here.
class TimeStamp(models.Model):
    """
    An abstract models which will be used in all models to save created and updated
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    """
    A custom manager for User model
    """

    def _create_user(self, password, is_staff, is_superuser, **extra_fields):
        user = self.model(is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        return self._create_user(password, False, False, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        user = self._create_user(password, True, True, **extra_fields)
        admin_group = Group.objects.get(name='admin')
        admin_group.user_set.add(user)
        user.role = 'admin'
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, TimeStamp):
    """
    Custom user model
    """

    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=200,null=True, unique=False)
    role = models.CharField(
        max_length=10, choices=constants.USER_ROLE_CHOICES, default="normal"
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_first_login = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    recieve_promotions = models.BooleanField(default=False)
    objects = CustomUserManager()
    objects_all = models.Manager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
