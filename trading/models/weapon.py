from django.db import models

class Weapon(models.Model):
    SWORD = 1
    STAFF = 2
    AXE = 3

    WEAPON_TYPES = [
        (SWORD, "Sword"),
        (STAFF, "Staff"),
        (AXE, "Axe"),
    ]

    type = models.PositiveSmallIntegerField(choices=WEAPON_TYPES)

    def __str__(self):
        return dict(self.WEAPON_TYPES).get(self.type, "Unknown")
    

class WeaponVariant(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name="variants")
    variant_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.variant_name} {self.weapon}"
    