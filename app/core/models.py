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

    def create_cashier(self, email, password):
        """
        Creates and save a new cashier
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_cashier = True
        user.is_manager = False
        user.is_superuser = False
        user.save(using=self._db)

        return user

    def create_manager(self, email, password):
        """
        Creates and save a new manager
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_cashier = True
        user.is_manager = True
        user.is_superuser = False
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a new super user
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_cashier = True
        user.is_manager = True
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
    is_cashier = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Unit(models.Model):
    """
    Unit of product
    """
    name = models.CharField(max_length=75)
    short_name = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category of product
    """
    name = models.CharField(max_length=225)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product in store
    """

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    unit_in_stock = models.FloatField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=4, decimal_places=2)
    reorder_level = models.FloatField()
    on_sale = models.BooleanField(default=False)

    unit = models.ForeignKey(
        'Unit',
        on_delete=models.RESTRICT
    )
    categories = models.ManyToManyField('Category')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """
    Supplier of products
    """

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Customer of the store
    """

    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
