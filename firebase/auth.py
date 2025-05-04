from firebase_admin import auth
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .config import db
import logging

logger = logging.getLogger(__name__)

async def verify_firebase_token(id_token_str: str):
    try:
        decoded_token = auth.verify_id_token(id_token_str)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

async def handle_google_auth(google_token: str):
    try:
        id_info = id_token.verify_oauth2_token(
            google_token,
            google_requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )
        
        # Check if user exists in Firebase
        try:
            user = auth.get_user_by_email(id_info['email'])
        except auth.UserNotFoundError:
            # Create new user if not exists
            user = auth.create_user(
                email=id_info['email'],
                display_name=id_info.get('name', ''),
                email_verified=True
            )
            # Store additional info in Firestore
            user_ref = db.collection("users").document(user.uid)
            user_ref.set({
                'email': id_info['email'],
                'name': id_info.get('name', ''),
                'created_at': firestore.SERVER_TIMESTAMP
            })
        
        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")