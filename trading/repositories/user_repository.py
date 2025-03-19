from trading.models import User

class UserRepository:
    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.filter(id=user_id).first()
