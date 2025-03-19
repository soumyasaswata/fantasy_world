from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ELF = 1
    WIZARD = 2
    DWARF = 3

    USER_TYPES = [
        (ELF, "Elf"),
        (WIZARD, "Wizard"),
        (DWARF, "Dwarf"),
    ]
    
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPES)

    groups = models.ManyToManyField(Group, related_name="trading_users")
    user_permissions = models.ManyToManyField(Permission, related_name="trading_user_permissions")