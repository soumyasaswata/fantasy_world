import json
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from trading.models import TradeOffer, User, Weapon, WeaponVariant, Inventory
from rest_framework.test import APIClient

class TradeOfferTestCase(TestCase):
    """Test cases for Trade Offer creation, acceptance, and rejection."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test cases (faster execution)."""
        cls.client = APIClient()

        # Create Users
        cls.sender = User.objects.create(username="gandalf", user_type=User.WIZARD)
        cls.receiver = User.objects.create(username="gimli", user_type=User.DWARF)

        # Create Weapons & Variants
        cls.sword = Weapon.objects.create(type=Weapon.SWORD)
        cls.staff = Weapon.objects.create(type=Weapon.STAFF)
        cls.red_sword = WeaponVariant.objects.create(weapon=cls.sword, variant_name="Red")
        cls.blue_staff = WeaponVariant.objects.create(weapon=cls.staff, variant_name="Blue")

        # Add Inventory
        Inventory.objects.create(user=cls.sender, weapon=cls.sword, variant=cls.red_sword, quantity=3)
        Inventory.objects.create(user=cls.receiver, weapon=cls.staff, variant=cls.blue_staff, quantity=2)

        # Create a pending trade offer
        cls.pending_trade = TradeOffer.objects.create(sender=cls.sender, receiver=cls.receiver, status=TradeOffer.PENDING, created_at=now())

    # ------------------ ✅ Trade Offer Creation ------------------
    def test_create_trade_offer(self):
        """Test successful trade offer creation."""
        data = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "offered_items": [{"weapon_id": self.sword.id, "variant_id": self.red_sword.id, "quantity": 2}],
            "requested_items": [{"weapon_id": self.staff.id, "variant_id": self.blue_staff.id, "quantity": 1}]
        }
        response = self.client.post(
            reverse("trade-offer-create"),
            data=json.dumps(data),  # 🔹 Ensure JSON serialization
            content_type="application/json"  # 🔹 Explicitly set JSON format
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("trade_offer_id", response.json())

    def test_create_trade_offer_with_invalid_weapon(self):
        """Test creating a trade offer with a non-existent weapon."""
        data = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "offered_items": [{"weapon_id": 999, "variant_id": self.red_sword.id, "quantity": 2}],  # Invalid weapon
            "requested_items": [{"weapon_id": self.staff.id, "variant_id": self.blue_staff.id, "quantity": 1}]
        }
        response = self.client.post(
            reverse("trade-offer-create"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_create_trade_offer_with_insufficient_inventory(self):
        """Test creating a trade offer when sender does not have enough inventory."""
        data = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "offered_items": [{"weapon_id": self.sword.id, "variant_id": self.red_sword.id, "quantity": 10}],  # Not enough inventory
            "requested_items": [{"weapon_id": self.staff.id, "variant_id": self.blue_staff.id, "quantity": 1}]
        }
        response = self.client.post(
            reverse("trade-offer-create"),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    # ------------------ ✅ Trade Offer Acceptance & Rejection ------------------
    def test_accept_trade_offer(self):
        """Test successful trade offer acceptance."""
        data = {"receiver_id": self.receiver.id, "action": "ACCEPT"}
        response = self.client.patch(
            reverse("trade-offer-update", args=[self.pending_trade.id]),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Accepted")

    def test_reject_trade_offer(self):
        """Test successful trade offer rejection."""
        data = {"receiver_id": self.receiver.id, "action": "REJECT"}
        response = self.client.patch(
            reverse("trade-offer-update", args=[self.pending_trade.id]),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Rejected")

    def test_accept_already_processed_offer(self):
        """Test trying to accept an already accepted/rejected trade."""
        accepted_trade = TradeOffer.objects.create(sender=self.sender, receiver=self.receiver, status=TradeOffer.ACCEPTED, created_at=now())
        data = {"receiver_id": self.receiver.id, "action": "ACCEPT"}
        response = self.client.patch(
            reverse("trade-offer-update", args=[accepted_trade.id]),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_trade_action(self):
        """Test sending an invalid action."""
        data = {"receiver_id": self.receiver.id, "action": "INVALID_ACTION"}
        response = self.client.patch(
            reverse("trade-offer-update", args=[self.pending_trade.id]),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_non_receiver_trying_to_accept_offer(self):
        """Test that only the receiver can accept/reject an offer."""
        another_user = User.objects.create(username="frodo", user_type=User.ELF)
        data = {"receiver_id": another_user.id, "action": "ACCEPT"}
        response = self.client.patch(
            reverse("trade-offer-update", args=[self.pending_trade.id]),
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
