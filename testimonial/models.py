from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Testimonial(models.Model):
    """
    User feedback and ratings for the platform.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="testimonial"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    feedback = models.TextField()
    designation = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="e.g. Resident, City Official, Student"
    )
    is_displayed = models.BooleanField(
        default=True, 
        db_index=True,
        help_text="Whether to show this testimonial on the frontend"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback by {self.user.email} - {self.rating} stars"
