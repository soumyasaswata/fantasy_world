from django.db import models
from .weapon import Weapon, WeaponVariant
from .user import User

class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    variant = models.ForeignKey(WeaponVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'weapon')  # Ensures a user has only one row per weapon type