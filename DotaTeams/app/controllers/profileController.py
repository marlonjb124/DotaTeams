from models.profile import Profile

def createPerfil(user_id: int):
    return Profile(user_id = user_id)