from trading.models import Weapon, WeaponVariant

class WeaponRepository:
    @staticmethod
    def get_weapon_by_id(weapon_id):
        return Weapon.objects.filter(id=weapon_id).first()

    @staticmethod
    def get_variant_by_id(variant_id):
        return WeaponVariant.objects.filter(id=variant_id).first()
