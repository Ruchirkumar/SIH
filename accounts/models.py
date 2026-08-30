from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom User model for the legalmetro project.
    Extends AbstractUser to include role-based access control.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        ENFORCEMENT_OFFICER = 'ENFORCEMENT_OFFICER', 'Enforcement Officer'
        VIEWER = 'VIEWER', 'Viewer'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text="Defines the user's permissions level within the legalmetro system."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
