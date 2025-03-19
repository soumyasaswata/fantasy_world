from rest_framework import serializers
from trading.models import TradeOffer, TradeItem, User, Inventory, Weapon, WeaponVariant

class TradeItemSerializer(serializers.Serializer):
    weapon_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)


class TradeOfferSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(write_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    sender_username = serializers.CharField(source="sender.username", read_only=True)
    receiver_username = serializers.CharField(source="receiver.username", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TradeOffer
        fields = ["id", "sender_id", "sender_username", "receiver_id", "receiver_username", "status", "status_display", "created_at"]

