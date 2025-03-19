# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from trading.models import User, Weapon, WeaponVariant, Inventory, TradeOffer, TradeItem

# class TradeTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()

#         # Create Users
#         self.elf = User.objects.create(username="legolas", user_type=User.ELF, email="legolas@middleearth.com")
#         self.wizard = User.objects.create(username="gandalf", user_type=User.WIZARD, email="gandalf@middleearth.com")

#         # Create Weapons
#         self.sword = Weapon.objects.create(type=Weapon.SWORD)
#         self.staff = Weapon.objects.create(type=Weapon.STAFF)

#         # Create Weapon Variants
#         self.red_sword = WeaponVariant.objects.create(weapon=self.sword, variant_name="Red")
#         self.blue_staff = WeaponVariant.objects.create(weapon=self.staff, variant_name="Blue")

#         # Assign Inventory
#         Inventory.objects.create(user=self.elf, weapon=self.sword, variant=self.red_sword, quantity=3)
#         Inventory.objects.create(user=self.wizard, weapon=self.staff, variant=self.blue_staff, quantity=2)

#     # def tearDown(self):
#     #     Inventory.objects.all().delete()
#     #     WeaponVariant.objects.all().delete()
#     #     Weapon.objects.all().delete()
#     #     User.objects.all().delete()
#     #     TradeOffer.objects.all().delete()
#     #     TradeItem.objects.all().delete()

#     def test_create_trade_offer(self):
#         url = reverse("trade-offer-create")
#         data = {
#             "sender_id": self.elf.id,
#             "receiver_id": self.wizard.id,
#             "offered_items": [{"weapon_id": self.sword.id, "variant_id": self.red_sword.id, "quantity": 1}],
#             "requested_items": [{"weapon_id": self.staff.id, "variant_id": self.blue_staff.id, "quantity": 1}]
#         }
#         response = self.client.post(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn("trade_offer_id", response.data)

#     def test_accept_trade_offer(self):
#         # Create a trade offer
#         trade_offer = TradeOffer.objects.create(sender=self.elf, receiver=self.wizard)
#         TradeItem.objects.create(offer=trade_offer, weapon=self.sword, variant=self.red_sword, quantity=1, is_offered_by_sender=True)
#         TradeItem.objects.create(offer=trade_offer, weapon=self.staff, variant=self.blue_staff, quantity=1, is_offered_by_sender=False)

#         url = reverse("trade-offer-update", args=[trade_offer.id])
#         data = {"receiver_id": self.wizard.id, "action": "ACCEPT"}
#         response = self.client.patch(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["status"], "Accepted")

#     def test_reject_trade_offer(self):
#         # Create a trade offer
#         trade_offer = TradeOffer.objects.create(sender=self.elf, receiver=self.wizard)
#         TradeItem.objects.create(offer=trade_offer, weapon=self.sword, variant=self.red_sword, quantity=1, is_offered_by_sender=True)
#         TradeItem.objects.create(offer=trade_offer, weapon=self.staff, variant=self.blue_staff, quantity=1, is_offered_by_sender=False)

#         url = reverse("trade-offer-update", args=[trade_offer.id])
#         data = {"receiver_id": self.wizard.id, "action": "REJECT"}
#         response = self.client.patch(url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["status"], "Rejected")

#     # def test_view_inventory(self):
#     #     url = reverse("inventory-view", args=[self.elf.id])
#     #     response = self.client.get(url)
#     #     self.assertEqual(response.status_code, status.HTTP_200_OK)
#     #     self.assertEqual(len(response.data), 1)
#     #     self.assertEqual(response.data[0]["weapon_name"], "Sword")
#     #     self.assertEqual(response.data[0]["variant"], "Red")
#     #     self.assertEqual(response.data[0]["quantity"], 3)