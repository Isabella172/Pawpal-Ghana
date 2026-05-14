from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import re
from django.core.exceptions import ValidationError


def validate_ghana_phone_number(value):
    pattern = r'^\+233\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError('Enter a valid Ghanaian phone number, e.g. +233240000000.')


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email address must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'owner')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'Pet owner'),
        ('groomer', 'Groomer'),
    ]

    username = None
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, validators=[validate_ghana_phone_number], unique=True)
    email = models.EmailField(unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'role']

    def __str__(self):
        return f"{self.email} - {self.role}"

    def is_groomer(self):
        return self.role == 'groomer'

    def is_owner(self):
        return self.role == 'owner'

