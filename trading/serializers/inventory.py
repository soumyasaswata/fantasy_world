from rest_framework import serializers
from trading.models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    weapon_name = serializers.CharField(source="weapon.get_type_display")  # Get readable name
    variant = serializers.CharField(source="variant.variant_name", required=False, allow_null=True)  # Get variant name

    class Meta:
        model = Inventory
        fields = ["weapon_name", "variant", "quantity"]
