from django.contrib import admin
from .models import User, Weapon, Inventory, TradeOffer, TradeItem, Ledger

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "user_type", "email", "is_staff", "is_active")
    search_fields = ("username", "email", "user_type")

@admin.register(Weapon)
class WeaponAdmin(admin.ModelAdmin):
    list_display = ("type", "get_variants")

    def get_variants(self, obj):
        return ", ".join(obj.variants.values_list("variant_name", flat=True)) or "No Variants"

    get_variants.short_description = "Variants"

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "weapon", "quantity")

@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "status", "created_at")
    list_filter = ("status",)

@admin.register(TradeItem)
class TradeItemAdmin(admin.ModelAdmin):
    list_display = ("offer", "weapon", "quantity", "is_offered_by_sender")

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ("trade_offer", "sender", "receiver", "weapon", "quantity", "created_at", "reversed")
    list_filter = ("reversed",)

