from django.utils import timezone
from django.db import models
from .user import User
from .weapon import Weapon, WeaponVariant

class TradeOffer(models.Model):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_offers")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_offers")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)

    def accept(self):
        self.status = self.ACCEPTED
        self.save()
    
    def reject(self):
        self.status = self.REJECTED
        self.save()


class TradeItem(models.Model):
    offer = models.ForeignKey(TradeOffer, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    variant = models.ForeignKey(WeaponVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    is_offered_by_sender = models.BooleanField(default=True)  # True = sender's item, False = receiver's item