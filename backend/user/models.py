"""This module defines class User"""
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    """This class defines createuser and createsuperuser methods."""
    def create_user(self, username, email, password, **other_fields):
        """This method creates a new user."""
        # pylint: disable=no-member

        if not username:
            raise ValueError('Username is required.')
        if not email:
            raise ValueError('Email is required.')
        if not password:
            raise ValueError('Password is required.')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, password=password, **other_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password, **other_fields):
        """This method creates a superuser user."""
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff set to true.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser set to true.')
        return self.create_user(username, email, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """This class defines the attributes of a user within the application."""
    id = models.CharField(default=uuid4, max_length=36,
                          unique=True, primary_key=True, editable=False)
    username = models.CharField(max_length=250, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, editable=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    class Meta:
        """
        db_table: Name of the table this class creates in the database.
        ordering: The order the instances of this model is displayed on the admin page.
        """
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        """This method returns a string representation of the instance of this class."""
        return f'{self.id} {self.username}'
