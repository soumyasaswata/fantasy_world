import logging
from django.db import transaction
from trading.models import TradeOffer, TradeItem, Inventory, Weapon, WeaponVariant, User
from trading.exceptions import TradeValidationError

logger = logging.getLogger(__name__)

class TradeService:
    @staticmethod
    def validate_trade_before_creation(sender_id, offered_items):
        """
        Ensures that the sender owns the weapons being offered BEFORE creating the trade.
        Expects offered_items as a list of dictionaries (from API request).
        """
        sender = User.objects.get(id=sender_id)

        if not offered_items:
            raise TradeValidationError("At least one item must be offered.")

        for item in offered_items:

            weapon = Weapon.objects.filter(id=item["weapon_id"]).first()
            variant = WeaponVariant.objects.filter(id=item["variant_id"]).first() if item.get("variant_id") else None
            
            if not weapon:
                raise TradeValidationError(f"Weapon with ID {item['weapon_id']} does not exist.")

            if variant and variant.weapon != weapon:
                raise TradeValidationError(f"Variant {variant.variant_name} does not belong to Weapon {weapon}.")

            inventory = Inventory.objects.filter(user=sender, weapon=weapon, variant=variant).first()
            
            if not inventory or inventory.quantity < item["quantity"]:
                raise TradeValidationError(f"User {sender.username} does not have enough {weapon.get_type_display()} {variant.variant_name if variant else 'No Variant'}.")

    @staticmethod
    def validate_trade_during_execution(user_id, trade_items):
        """
        Ensures that the user has enough inventory to fulfill the trade when the trade is executed.
        Expects trade_items as a QuerySet of TradeItem objects.
        """
        user = User.objects.get(id=user_id)

        inventory_items = Inventory.objects.filter(user=user).select_related("weapon", "variant")
        
        inventory_dict = {
            (inv.weapon.id, inv.variant.id if inv.variant else None): inv.quantity
            for inv in inventory_items
        }

        for item in trade_items:
            key = (item.weapon.id, item.variant.id if item.variant else None)
            available_quantity = inventory_dict.get(key, 0)

            if available_quantity < item.quantity:
                raise TradeValidationError(f"User {user.username} does not have enough {item.weapon.get_type_display()} {item.variant.variant_name if item.variant else 'No Variant'}.")


    @staticmethod
    def create_trade_offer(sender_id, receiver_id, offered_items, requested_items):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        TradeService.validate_trade_before_creation(sender_id, offered_items)

        with transaction.atomic():
            trade_offer = TradeOffer.objects.create(sender=sender, receiver=receiver)
            logger.info(f"Trade offer created with ID {trade_offer.id}")

            # assuming less trade items are created
            trade_items = []

            for item in offered_items:
                weapon = Weapon.objects.get(id=item["weapon_id"])
                variant = WeaponVariant.objects.get(id=item["variant_id"]) if item.get("variant_id") else None
                trade_items.append(TradeItem(
                    offer=trade_offer, weapon=weapon, variant=variant, quantity=item["quantity"], is_offered_by_sender=True
                ))

            for item in requested_items:
                weapon = Weapon.objects.get(id=item["weapon_id"])
                variant = WeaponVariant.objects.get(id=item["variant_id"]) if item.get("variant_id") else None
                trade_items.append(TradeItem(
                    offer=trade_offer, weapon=weapon, variant=variant, quantity=item["quantity"], is_offered_by_sender=False
                ))

            TradeItem.objects.bulk_create(trade_items)

        return trade_offer
    
    @staticmethod
    def process_trade_offer(trade_offer_id, receiver_id, action):
        """
        Accept or reject a trade offer.
        """
        trade_offer = TradeOffer.objects.filter(id=trade_offer_id, status=TradeOffer.PENDING).first()

        if not trade_offer:
            raise TradeValidationError(f"Trade offer {trade_offer_id} does not exist or is already processed.")

        if trade_offer.receiver.id != receiver_id:
            raise TradeValidationError("Only the receiver can accept or reject this trade.")

        if action.upper() == "ACCEPT":
            TradeService._execute_trade(trade_offer)
            trade_offer.accept()

        elif action.upper() == "REJECT":
            trade_offer.reject()

        return trade_offer

    @staticmethod
    @transaction.atomic
    def _execute_trade(trade_offer):
        """
        Transfers inventory between sender and receiver when a trade is accepted.
        """
        trade_items = TradeItem.objects.filter(offer=trade_offer)

        # Validate that both users have enough inventory BEFORE executing the trade
        TradeService.validate_trade_during_execution(trade_offer.sender.id, trade_items.filter(is_offered_by_sender=True))
        TradeService.validate_trade_during_execution(trade_offer.receiver.id, trade_items.filter(is_offered_by_sender=False))

        for item in trade_items.filter(is_offered_by_sender=True):
            sender_inventory = Inventory.objects.get(user=trade_offer.sender, weapon=item.weapon, variant=item.variant)
            sender_inventory.quantity -= item.quantity
            sender_inventory.save()

            receiver_inventory, created = Inventory.objects.get_or_create(
                user=trade_offer.receiver, weapon=item.weapon, variant=item.variant,
                defaults={"quantity": 0}
            )
            receiver_inventory.quantity += item.quantity
            receiver_inventory.save()

        for item in trade_items.filter(is_offered_by_sender=False):
            receiver_inventory = Inventory.objects.get(user=trade_offer.receiver, weapon=item.weapon, variant=item.variant)
            receiver_inventory.quantity -= item.quantity
            receiver_inventory.save()

            sender_inventory, created = Inventory.objects.get_or_create(
                user=trade_offer.sender, weapon=item.weapon, variant=item.variant,
                defaults={"quantity": 0}
            )
            sender_inventory.quantity += item.quantity
            sender_inventory.save()
