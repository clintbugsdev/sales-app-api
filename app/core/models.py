from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

#
# class Category(models.Model):
#     """
#     Category of product
#     """
#     name = models.CharField(max_length=225)
#
#     def __str__(self):
#         return self.name
#
#
# class Unit(models.Model):
#     """
#     Unit of product
#     """
#     name = models.CharField(max_length=75)
#     short_name = models.CharField(max_length=25)
#
#     def __str__(self):
#         return self.name
#
#
# class Customer(models.Model):
#     """
#     Customer of store
#     """
#     code = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     birthdate = models.DateField()
#     gender = models.CharField(max_length=25)
#     contact = models.CharField(max_length=255)
#     address = models.CharField(max_length=255)
#     email = models.EmailField(max_length=255)
#
#     def __str__(self):
#         return self.name
