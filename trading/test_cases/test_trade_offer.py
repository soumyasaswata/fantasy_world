from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from trading.models import TradeOffer, User, Weapon, WeaponVariant, Inventory
from rest_framework.test import APIClient


class TradeOfferHistoryTestCase(TestCase):
    """Test cases for Trade Offer History API"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test cases (faster than setUp)."""
        cls.client = APIClient()

        # Create Users
        cls.sender = User.objects.create(username="gandalf", user_type=User.WIZARD)
        cls.receiver = User.objects.create(username="gimli", user_type=User.DWARF)

        # Create Weapons & Variants
        cls.sword = Weapon.objects.create(type=1)  # Sword
        cls.staff = Weapon.objects.create(type=2)  # Staff
        cls.red_sword = WeaponVariant.objects.create(weapon=cls.sword, variant_name="Red")
        cls.blue_staff = WeaponVariant.objects.create(weapon=cls.staff, variant_name="Blue")

        # Add Inventory
        Inventory.objects.create(user=cls.sender, weapon=cls.sword, variant=cls.red_sword, quantity=3)
        Inventory.objects.create(user=cls.receiver, weapon=cls.staff, variant=cls.blue_staff, quantity=2)

        # Create Trade Offers
        cls.trade1 = TradeOffer.objects.create(sender=cls.sender, receiver=cls.receiver, status=TradeOffer.ACCEPTED, created_at=now())
        cls.trade2 = TradeOffer.objects.create(sender=cls.sender, receiver=cls.receiver, status=TradeOffer.REJECTED, created_at=now())

    def test_get_all_trade_offers_for_user(self):
        """Test retrieving all trade offers for a user"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_sent_trade_offers(self):
        """Test retrieving only sent trade offers"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.sender.id, 'type': 'sent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_received_trade_offers(self):
        """Test retrieving only received trade offers"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'type': 'received'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_accepted_trade_offers(self):
        """Test retrieving only accepted trade offers"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'status': TradeOffer.ACCEPTED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['status_display'], "Accepted")

    def test_get_trade_offers_with_start_date(self):
        """Test retrieving trade offers after a certain date"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'start_date': '2025-03-16'})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_get_trade_offers_with_end_date(self):
        """Test retrieving trade offers before a certain date"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'end_date': '2025-03-16'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)  # No trades before this date

    def test_get_trade_offers_within_date_range(self):
        """Test retrieving trade offers within a specific date range"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'start_date': '2025-03-16', 'end_date': '2026-03-19'})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_invalid_user_id(self):
        """Test fetching trade offers for a non-existent user"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': 9999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_status(self):
        """Test fetching trade offers with an invalid status"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'status': 99})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_type_parameter(self):
        """Test fetching trade offers with an invalid type parameter"""
        response = self.client.get(reverse('trade-offer-history'), {'user_id': self.receiver.id, 'type': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid type parameter"})
