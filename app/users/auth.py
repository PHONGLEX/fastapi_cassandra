import datetime
from datetime import timedelta
from jose import jwt, ExpiredSignatureError
from .models import User
from app import config


settings = config.get_settings()


def authenticate(email, password):
    try:
        user_obj:User = User.objects.get(email=email)
    except Exception as e:
        return None
    
    if not user_obj.verify_password(password):
        return None
    return user_obj    


def login(user_obj, expires=5):
    raw_data = {
        "user_id": f"{user_obj.user_id}",
        "role": "admin",
        "exp": datetime.datetime.utcnow() + timedelta(seconds=expires)
    }
    return jwt.encode(raw_data, settings.secret_key, algorithm=settings.jwt_algorithm)
    

def verify_user_id(token):
    data = {}
    try:
        data = jwt.decode(token, settings.secret_key, algorithm=[settings.jwt_algorithm])
    except ExpiredSignatureError as e:
        pass
    except:
        pass
    if 'user_id' not in data:
        return None
    return data