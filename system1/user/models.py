from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    # Method to create a normal user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)  # Normalize the email address (e.g., lowercase)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set the password (hashed)
        user.save(using=self._db)  # Save the user to the database
        return user

    # Method to create a superuser (admin user)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)  # Superusers must be staff
        extra_fields.setdefault('is_superuser', True)  # Superusers must have superuser rights
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')

        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    middle_name = models.CharField(max_length=50, blank=True,null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'  # Use the email field as the username
    REQUIRED_FIELDS = []  # No required fields

    objects = CustomUserManager()

    def __str__(self):
        return self.email
       
