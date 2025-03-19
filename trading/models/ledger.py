from django.db import models
from .trade import TradeOffer
from .user import User
from .weapon import Weapon, WeaponVariant

class Ledger(models.Model):
    trade_offer = models.ForeignKey(TradeOffer, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ledger_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ledger_receiver")
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)
    variant = models.ForeignKey(WeaponVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    reversed = models.BooleanField(default=False)  # Marks if a trade was reversed