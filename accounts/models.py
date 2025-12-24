import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

def user_profile_pic_path(instance, filename):
    # Get the file extension (e.g., .jpg, .png)
    ext = filename.split('.')[-1]
    # Name the file using the user's ID or temporary UUID if ID isn't set yet
    filename = f"{instance.id if instance.id else 'temp'}.{ext}"
    return os.path.join('profile_pics', filename)

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Default login field for Django's internal auth
    REQUIRED_FIELDS = ['username', 'fullname']

    def __str__(self):
        return self.email