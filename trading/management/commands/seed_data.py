from django.core.management.base import BaseCommand
from django.db import connection
from trading.models import User, Weapon, WeaponVariant, Inventory, TradeOffer

class Command(BaseCommand):
    help = "Seeds the database with sample users, weapons, and inventory."

    def handle(self, *args, **kwargs):
        Inventory.objects.all().delete()
        WeaponVariant.objects.all().delete()
        Weapon.objects.all().delete()
        User.objects.all().delete()
        TradeOffer.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE trading_user_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE trading_weapon_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE trading_weaponvariant_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE trading_inventory_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE trading_tradeoffer_id_seq RESTART WITH 1;")
            cursor.execute("ALTER SEQUENCE trading_tradeitem_id_seq RESTART WITH 1;")

        # Create Users
        elf = User.objects.create(username="soumya", user_type=User.ELF, email="soumya@gmail.com")
        wizard = User.objects.create(username="smruti", user_type=User.WIZARD, email="smruti@gmail.com")
        dwarf = User.objects.create(username="shradha", user_type=User.DWARF, email="shradha@gmail.com")

        self.stdout.write(self.style.SUCCESS(f"Users Created: {elf}, {wizard}, {dwarf}"))

        # Create Weapons
        sword = Weapon.objects.create(type=Weapon.SWORD)
        staff = Weapon.objects.create(type=Weapon.STAFF)
        axe = Weapon.objects.create(type=Weapon.AXE)

        self.stdout.write(self.style.SUCCESS(f"Weapons Created: {sword}, {staff}, {axe}"))

        # Create Weapon Variants
        red_sword = WeaponVariant.objects.create(weapon=sword, variant_name="Red")
        blue_staff = WeaponVariant.objects.create(weapon=staff, variant_name="Blue")
        green_axe = WeaponVariant.objects.create(weapon=axe, variant_name="Green")

        self.stdout.write(self.style.SUCCESS(f"Weapon Variants Created: {red_sword}, {blue_staff}, {green_axe}"))

        # Assign Inventory
        Inventory.objects.create(user=elf, weapon=sword, variant=red_sword, quantity=3)
        Inventory.objects.create(user=wizard, weapon=staff, variant=blue_staff, quantity=2)
        Inventory.objects.create(user=dwarf, weapon=axe, variant=green_axe, quantity=4)

        self.stdout.write(self.style.SUCCESS("Sample Inventory Populated Successfully!"))
