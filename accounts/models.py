# python
import os.path

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    UserManager,
)

from accounts.managers import CustomUserManager


def profile_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"user_{instance.id}_profile.{ext}"
    return os.path.join("profile_pics", filename)


# Alias kept for backward compatibility with existing migrations
def user_profile_pic_path(instance, filename):
    return profile_image_upload_path(instance, filename)


class User(AbstractBaseUser, PermissionsMixin):
    # make email a index for faster lookups
    email = models.EmailField(unique=True, db_index=True, null=False, blank=False)
    password = models.CharField(
        max_length=128,
        null=False,
        blank=False,
    )

    first_name = models.CharField(max_length=30, null=False, blank=False, default="")
    last_name = models.CharField(max_length=30, null=True, blank=True)

    phone_number = models.CharField(blank=True, max_length=15, null=True)
    profile_pic = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    def save(self, *args, **kwargs):
        """
        Ensure the profile image filename uses the instance id.
        If the instance has no pk yet, save once without the image to get an id,
        then restore the image name and save again updating only profile_pic.
        """
        profile = self.profile_pic
        if profile and not self.pk:
            tmp = profile
            self.profile_pic = None
            super().save(*args, **kwargs)  # get a pk
            self.profile_pic = tmp
            self.profile_pic.name = profile_image_upload_path(self, tmp.name)
            super().save(update_fields=["profile_pic"])
            return

        if profile:
            self.profile_pic.name = profile_image_upload_path(self, profile.name)

        super().save(*args, **kwargs)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

    def __str__(self):
        return self.email
