import json
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now, timedelta
from trading.models import TradeOffer, User, Weapon, WeaponVariant
from django.utils.timezone import make_aware
from datetime import datetime

class TradeOfferHistoryTestCase(TestCase):
    """Test cases for Trade Offer History API."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all test cases (faster execution)."""
        cls.sender = User.objects.create(username="gandalf", user_type=User.WIZARD)
        cls.receiver = User.objects.create(username="gimli", user_type=User.DWARF)

        # 🔹 Ensure trade offers are created within the test range (March 8 - March 13, 2025)
        cls.trade_accepted = TradeOffer.objects.create(
            sender=cls.sender, receiver=cls.receiver, 
            status=TradeOffer.ACCEPTED, 
            created_at=make_aware(datetime(2025, 3, 10, 12, 0))  # ✅ Inside range
        )

        cls.trade_rejected = TradeOffer.objects.create(
            sender=cls.sender, receiver=cls.receiver, 
            status=TradeOffer.REJECTED, 
            created_at=make_aware(datetime(2025, 3, 12, 15, 30))  # ✅ Inside range
        )

        cls.trade_pending = TradeOffer.objects.create(
            sender=cls.sender, receiver=cls.receiver, 
            status=TradeOffer.PENDING, 
            created_at=make_aware(datetime(2025, 3, 18, 10, 45))  # ❌ OUTSIDE RANGE
        )

    def test_get_all_trade_offers(self):
        """Test retrieving all trade offers for a user."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.receiver.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)  # Expecting 3 trade offers in total

    def test_get_sent_trade_offers(self):
        """Test retrieving only sent trade offers."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.sender.id, "type": "sent"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_get_received_trade_offers(self):
        """Test retrieving only received trade offers."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.receiver.id, "type": "received"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_filter_by_status(self):
        """Test filtering trade offers by status."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.receiver.id, "status": TradeOffer.ACCEPTED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_filter_by_date_range(self):
        """Test filtering trade offers by date range."""
        response = self.client.get(reverse("trade-offer-history"), {
            "user_id": self.receiver.id, 
            "start_date": "2025-03-08", 
            "end_date": "2025-03-13"
        })

        self.assertEqual(response.status_code, 200)

        print("response", response.json())

        trades = TradeOffer.objects.all()

        for trade in trades:
            print(trade.created_at)

        self.assertEqual(len(response.json()), 2)


    def test_invalid_user_id(self):
        """Test fetching trade offers for a non-existent user."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": 9999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_status(self):
        """Test fetching trade offers with an invalid status."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.receiver.id, "status": 99})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_type_parameter(self):
        """Test fetching trade offers with an invalid type parameter."""
        response = self.client.get(reverse("trade-offer-history"), {"user_id": self.receiver.id, "type": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid type parameter"})
