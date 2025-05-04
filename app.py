import os
import logging
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Body, Header, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional, List, Dict, Any
import re # Import regex for extracting YouTube ID

import firebase_admin
from firebase_admin import credentials, auth, db as admin_db
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


import modules.gemini_api as llm


# Load environment variables from .env file
load_dotenv()

# --- Firebase Initialization ---

#SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "serviceAccountKey.json")
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"
try:
    firebase_admin.get_app()
    logger = logging.getLogger(__name__)
    logger.info("Firebase Admin SDK already initialized.")
except ValueError:
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://databade-recom-default-rtdb.europe-west1.firebasedatabase.app"
        })
        logger = logging.getLogger(__name__)
        logger.info("Firebase Admin SDK initialised successfully.")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")


rt_db = None
try:
    rt_db = admin_db.reference('/')
except NameError:
    logger.error("Firebase Admin SDK not initialized, rt_db is not available.")


# --- FastAPI setup ---
app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "a_very_secret_key_that_should_be_changed"), # !!! CHANGE THIS IN .env !!!
    session_cookie="session",
    https_only=os.getenv("HTTPS_ONLY", "False").lower() == "true"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)

# --- Helper function to parse potential list strings ---
def parse_list_string(list_str: str) -> List[Any]:
    """Safely parses a string that might be a JSON list."""
    if not list_str:
        return []
    try:
        cleaned_str = list_str.strip().replace("'", '"')
        if cleaned_str.startswith('[') and cleaned_str.endswith(']'):
            return json.loads(cleaned_str)
        else:
            return [item.strip() for item in list_str.split(',')]
    except json.JSONDecodeError:
        return [item.strip() for item in list_str.split(',')]
    except Exception as e:
        logger.warning(f"Unexpected error parsing list string '{list_str}': {e}")
        return [list_str]

# --- Helper function to extract YouTube video ID ---
def extract_youtube_id(url: str) -> Optional[str]:
    """Extracts the YouTube video ID from a given URL."""
    if not url:
        return None
    # Regex for various YouTube URL formats - Using raw string (r"...") to fix SyntaxWarning
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = re.match(youtube_regex, url)
    if match:
        return match.group(6)
    return None


# --- Auth helpers ---

def get_session_user(request: Request):
    """Retrieves user info from the session."""
    return request.session.get("user")

def require_user(request: Request):
    """Dependency to protect routes, redirects to login if no user in session."""
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            headers={"Location": "/auth/login"})
    return user

# --- Google sign-in endpoint (Receives ID token from client) ---
@app.post("/auth/google")
async def google_login(request: Request, payload: dict = Body(...)):
    """Handles Google Sign-In by verifying the ID token and setting session."""
    logger.info(f"Received payload for Google login: {payload}")

    token = payload.get("id_token")
    if not token:
        logger.warning("Google login failed: Missing ID token in payload.")
        raise HTTPException(status_code=400, detail="Missing Google ID token")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "433799197630-60ejnft78h486qu84vn1p05rv5i8iuhh.apps.googleusercontent.com")
    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID environment variable not set.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server configuration error.")

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        try:
            user = auth.get_user_by_email(idinfo["email"])
            logger.info(f"Found existing Firebase user for email: {idinfo['email']}")
        except auth.UserNotFoundError:
            logger.info(f"Creating new Firebase user for email: {idinfo['email']}")
            user = auth.create_user(
                email=idinfo["email"],
                display_name=idinfo.get("name", ""),
                email_verified=idinfo.get("email_verified", False),
            )
            if rt_db:
                rt_db.child("users").child(user.uid).set({
                    "email": user.email,
                    "name":  user.display_name,
                    "photo_url": idinfo.get("picture", ""),
                    "provider": "google.com",
                    "created_at": admin_db.SERVER_TIMESTAMP,
                    "Travaux_Collaboratifs": 0,
                    "Coéquipiers": [],
                    "Communautés": [],
                    "Nombre_Interactions": 0,
                    "Compétences": [],
                    "Centres_d'Intérêt": [],
                    "Derniers_Cours_Interagis": [],
                    "title": "",
                    "bio": "",
                    "linkedin": "",
                    "website": "",
                    "location": "",
                    "notify_email": True,
                    "notify_push": False,
                    "notify_club": True
                })
                logger.info(f"Initial profile created in RTDB for new Google user: {user.uid}")
            else:
                 logger.warning("RTDB not initialized. Skipping initial profile creation for Google user.")


        request.session["user"] = {
            "uid":   user.uid,
            "email": user.email,
            "name":  user.display_name,
            "provider": "google.com"
        }
        logger.info(f"Session created for user: {user.uid}")


        return JSONResponse({"status": "ok", "message": "Google login successful"})

    except ValueError as e:
        logger.warning(f"Invalid Google token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {e}")
    except Exception as e:
        logger.error(f"Google login failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google login failed")


# --- GitHub sign-in endpoint (Receives ID token from client) ---
@app.post("/auth/github")
async def github_login(request: Request, payload: dict = Body(...)):
    """Handles GitHub Sign-In by verifying the ID token and setting session."""
    logger.info(f"Received payload for GitHub login: {payload}")

    token = payload.get("id_token")
    if not token:
        logger.warning("GitHub login failed: Missing ID token in payload.")
        raise HTTPException(status_code=400, detail="Missing GitHub ID token")

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        logger.info(f"ID token verified for UID: {uid} (GitHub auth)")

        user = auth.get_user(uid)
        logger.info(f"Retrieved Firebase user object for UID: {uid}")

        provider_id = 'github.com'
        if user.provider_data and user.provider_data[0]:
             provider_id = user.provider_data[0].provider_id

        email = decoded_token.get('email')
        name = decoded_token.get('name', user.display_name)
        photo_url = decoded_token.get('picture', user.photo_url)

        if rt_db:
            user_ref = rt_db.child("users").child(user.uid)
            user_data = user_ref.get()

            if not user_data:
                 logger.info(f"Creating initial profile in RTDB for new GitHub user: {user.uid}")
                 user_ref.set({
                     "email": email,
                     "name": name,
                     "photo_url": photo_url,
                     "provider": provider_id,
                     "created_at": admin_db.SERVER_TIMESTAMP,
                     "Travaux_Collaboratifs": 0,
                     "Coéquipiers": [],
                     "Communautés": [],
                     "Nombre_Interactions": 0,
                     "Compétences": [],
                     "Centres_d'Intérêt": [],
                     "Derniers_Cours_Interagis": [],
                     "title": "",
                     "bio": "",
                     "linkedin": "",
                     "website": "",
                     "location": "",
                     "notify_email": True,
                     "notify_push": False,
                     "notify_club": True
                 })
            else:
                 logger.info(f"Profile already exists for GitHub user: {user.uid}, updating basic info.")
                 update_data = {
                     "email": email if email is not None else user_data.get("email"),
                     "name": name,
                     "photo_url": photo_url if photo_url is not None else user_data.get("photo_url"),
                     "provider": provider_id
                 }
                 user_ref.update(update_data)


        request.session["user"] = {
            "uid": user.uid,
            "email": email,
            "name": name,
            "provider": provider_id
        }
        logger.info(f"Session created for GitHub user: {user.uid}")

        return JSONResponse({"status": "ok", "message": "GitHub login successful"})

    except ValueError as e:
        logger.warning(f"Invalid GitHub token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid GitHub token: {e}")
    except Exception as e:
        logger.error(f"GitHub login failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GitHub login failed")


# --- Authentication Routes ---

@app.get("/auth/login")
async def login_form(request: Request):
    """Renders the login form page."""
    if get_session_user(request):
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("auth.html", {
        "request": request,
        "show_login": True,
        "error": request.session.pop("error", None)
    })

@app.post("/auth/login")
async def firebase_login(
    request: Request,
    authorization: Optional[str] = Header(None),
    payload: Optional[dict] = Body(None)
):
    """Handles email/password login by verifying ID token and setting session."""
    id_token_str = None

    if authorization and authorization.startswith("Bearer "):
        id_token_str = authorization.split(" ")[1]
        logger.info("Received ID token from Authorization header.")
    elif payload and "id_token" in payload:
        id_token_str = payload["id_token"]
        logger.info("Received ID token from request body.")


    if not id_token_str:
        logger.warning("Login failed: Missing ID token in header or body.")
        request.session["error"] = "Authentication failed: Missing credentials."
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        decoded_token = auth.verify_id_token(id_token_str)
        uid = decoded_token['uid']
        logger.info(f"ID token verified for UID: {uid}")

        user = auth.get_user(uid)

        provider_id = 'email/password'
        if user.provider_data and user.provider_data[0]:
             provider_id = user.provider_data[0].provider_id


        user_info = {
            "uid": user.uid,
            "email": user.email,
            "name": decoded_token.get("name", user.display_name),
            "provider": provider_id
        }

        # Optionally update RTDB profile data if needed (e.g., last login time)
        # if rt_db:
        #     rt_db.child("users").child(user_info['uid']).update({"last_login": admin_db.SERVER_TIMESTAMP})

        request.session["user"] = user_info
        logger.info(f"Session created for user: {user.uid}")

        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Firebase login failed: {e}")
        request.session["error"] = f"Authentication failed: {e}"
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/auth/register")
async def register_form(request: Request):
    """Renders the registration form page."""
    if get_session_user(request):
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("auth.html", {
        "request": request,
        "show_login": False,
        "error": request.session.pop("error", None)
    })

@app.post("/auth/register")
async def firebase_register(
    request: Request,
    authorization: Optional[str] = Header(None),
    payload: Optional[dict] = Body(None)
):
    """Handles email/password registration by verifying ID token and setting session."""
    id_token_str = None

    if authorization and authorization.startswith("Bearer "):
        id_token_str = authorization.split(" ")[1]
        logger.info("Received ID token from Authorization header for registration.")
    elif payload and "id_token" in payload:
        id_token_str = payload["id_token"]
        logger.info("Received ID token from request body for registration.")

    name = payload.get("name", "") if payload else ""


    if not id_token_str:
        logger.warning("Registration failed: Missing ID token in header or body.")
        request.session["error"] = "Registration failed: Missing credentials."
        return RedirectResponse("/auth/register", status_code=status.HTTP_303_SEE_OTHER)

    try:
        decoded_token = auth.verify_id_token(id_token_str)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        logger.info(f"ID token verified for UID: {uid} during registration.")

        user = auth.get_user(uid)

        provider_id = 'email/password'
        if user.provider_data and user.provider_data[0]:
             provider_id = user.provider_data[0].provider_id


        if rt_db:
            user_ref = rt_db.child("users").child(user.uid)
            user_data = user_ref.get()
            if not user_data:
                 user_ref.set({
                     "email": email,
                     "name": name or user.display_name,
                     "provider": provider_id,
                     "created_at": admin_db.SERVER_TIMESTAMP,
                     "Travaux_Collaboratifs": 0,
                     "Coéquipiers": [],
                     "Communautés": [],
                     "Nombre_Interactions": 0,
                     "Compétences": [],
                     "Centres_d'Intérêt": [],
                     "Derniers_Cours_Interagis": [],
                     "title": "",
                     "bio": "",
                     "linkedin": "",
                     "website": "",
                     "location": "",
                     "notify_email": True,
                     "notify_push": False,
                     "notify_club": True
                 })
                 logger.info(f"Initial profile created in RTDB for user: {user.uid}")
            else:
                 logger.info(f"Profile already exists for user: {user.uid}, skipping initial creation.")


        request.session["user"] = {
            "uid": user.uid,
            "email": email,
            "name": name or user.display_name,
            "provider": provider_id
        }
        logger.info(f"Session created for user: {user.uid} after registration.")

        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        logger.error(f"Firebase registration backend failed: {e}")
        request.session["error"] = f"Registration failed: {e}"
        return RedirectResponse("/auth/register", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/auth/logout")
async def logout(request: Request):
    """Clears the server-side session and redirects to login."""
    request.session.clear()
    logger.info("User session cleared. Redirecting to login.")
    return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)


# --- Core Routes ---
@app.get("/")
async def home(
    request: Request,
    user=Depends(get_session_user),
    page: int = Query(1, ge=1), # Add pagination query parameter
    per_page: int = Query(6, ge=1) # Items per page
):
    """Renders the homepage with recommendations and paginated courses."""
    data = {"request": request, "user": user}
    all_contents_raw = None
    all_contents_list = [] # Use a list to store content items
    recommendations = []
    general_courses = []
    total_courses = 0
    total_pages = 0
    current_page = page

    if rt_db:
        try:
            # Fetch all content
            all_contents_raw = rt_db.child("contents").get()

            # --- Handle Firebase returning a list or dictionary ---
            if isinstance(all_contents_raw, dict):
                # If it's a dictionary, convert its values to a list
                all_contents_list = list(all_contents_raw.values())
                logger.info("Firebase /contents node returned a dictionary, converted to list.")
            elif isinstance(all_contents_raw, list):
                # If it's already a list, use it directly
                all_contents_list = all_contents_raw
                logger.info("Firebase /contents node returned a list.")
            elif all_contents_raw is None:
                 logger.info("Firebase /contents node is empty.")
                 all_contents_list = [] # Ensure it's an empty list
            else:
                logger.error(f"Firebase /contents node returned unexpected type: {type(all_contents_raw)}")
                all_contents_list = [] # Default to empty list
            # --- End of handling ---

            total_courses = len(all_contents_list)
            total_pages = (total_courses + per_page - 1) // per_page # Calculate total pages

            # Sort the list of content dictionaries by rating (descending)
            sorted_contents_list = sorted(
                all_contents_list,
                key=lambda item: item.get("Rating", 0), # Sort by 'Rating', default to 0 if missing
                reverse=True
            )

            # Implement pagination by slicing the sorted list
            start_index = (current_page - 1) * per_page
            end_index = start_index + per_page
            paginated_contents = sorted_contents_list[start_index:end_index]

            # Add YouTube embed URLs and implicit 'id' (list index) to each item
            general_courses = []
            # We need the original index for the ID, so let's re-process based on the paginated slice
            # Find the starting index of the paginated slice within the original list to get correct IDs
            # This is a bit complex if the original list order isn't guaranteed, but assuming it is:
            # A more robust way is to add the index during the initial list creation if converting from dict,
            # or rely on a unique ID field if it existed.
            # Given the user's data is a list without explicit IDs, we'll use the index *within the sorted list* for now
            # and add a warning that this might not map to stable IDs if the source changes.
            logger.warning("Using list index as content ID for display. This may not be stable.")
            for index, course_data in enumerate(paginated_contents):
                 course_with_id = course_data.copy() # Create a copy to add 'id'
                 # Use the index within the paginated slice as the ID for display/links
                 course_with_id['id'] = start_index + index # Use the index relative to the full sorted list

                 youtube_id = extract_youtube_id(course_data.get("Link"))
                 if youtube_id:
                     # Construct the embed URL using the extracted ID
                     course_with_id["EmbedLink"] = f"https://www.youtube.com/embed/{youtube_id}"
                 else:
                     course_with_id["EmbedLink"] = None

                 general_courses.append(course_with_id)


            logger.info(f"Fetched {total_courses} contents, displaying page {current_page} with {len(general_courses)} items.")

            # Fetch user profile and generate recommendations if user is logged in
            if user:
                user_profile = rt_db.child("users").child(user['uid']).get() or {}
                # Pass the raw data (list or dict) to the recommendation function
                recommendations = generate_recommendations(user_profile, all_contents_raw)
                logger.info(f"Fetched and generated {len(recommendations)} recommendations for user {user['uid']}.")

        except Exception as e:
             logger.error(f"Failed to fetch data or generate recommendations: {e}")

    else:
        logger.warning("Realtime Database not initialized. Cannot fetch data.")


    data["recommendations"] = recommendations
    data["general_courses"] = general_courses
    data["total_pages"] = total_pages
    data["current_page"] = current_page
    data["per_page"] = per_page # Pass per_page to the template for pagination links


    return templates.TemplateResponse("index.html", data)

@app.get("/profile")
async def profile_page(request: Request, user=Depends(require_user)):
    
    """Renders the profile page, requires authentication."""
    profile_data = {}
    coequipiers_details = []
    interacted_courses_details = []
    recommendations = []
    all_contents_raw = None # Fetch raw data
    all_contents_list = [] # Use a list for content items

    if rt_db:
        try:
            user_profile_ref = rt_db.child("users").child(user['uid'])
            profile_data = user_profile_ref.get() or {}
            logger.info(f"Fetched profile data for user {user['uid']}.")

            # Fetch all content for recommendations and interacted courses
            all_contents_raw = rt_db.child("contents").get()

            # --- Handle Firebase returning a list or dictionary ---
            if isinstance(all_contents_raw, dict):
                all_contents_list = list(all_contents_raw.values())
                logger.info("Firebase /contents node returned a dictionary in profile route, converted to list.")
            elif isinstance(all_contents_raw, list):
                all_contents_list = all_contents_raw
                logger.info("Firebase /contents node returned a list in profile route.")
            elif all_contents_raw is None:
                 logger.info("Firebase /contents node is empty in profile route.")
                 all_contents_list = []
            else:
                logger.error(f"Firebase /contents node returned unexpected type in profile route: {type(all_contents_raw)}")
                all_contents_list = []
            # --- End of handling ---


            coequipiers_ids = profile_data.get("Coéquipiers", [])
            if coequipiers_ids:
                all_users = rt_db.child("users").get() or {}
                coequipiers_details = [
                    {"ID_Étudiant": uid, "Nom": user_info.get("name", f"User {uid}")}
                    for uid, user_info in all_users.items() if str(uid) in [str(id) for id in coequipiers_ids] # Ensure string comparison
                ]
                logger.info(f"Fetched details for {len(coequipiers_details)} coéquipiers.")

            interacted_course_ids = profile_data.get("Derniers_Cours_Interagis", [])
            if interacted_course_ids and all_contents_list: # Check if all_contents_list is not empty
                 # If contents is a list, the IDs in Derniers_Cours_Interagis are likely list indices
                 interacted_courses_details = []
                 for cid in interacted_course_ids:
                      try:
                           # Attempt to get the content item using the ID as an index
                           content_item = all_contents_list[int(cid)]
                           if isinstance(content_item, dict):
                                interacted_courses_details.append({
                                     "ID_Étudiant": cid, # Use the original ID/index
                                     "Title": content_item.get("Title", f"Course {cid}"),
                                     "Link": content_item.get("Link", "#")
                                })
                           else:
                               logger.warning(f"Content item at index {cid} is not a dictionary.")
                      except (IndexError, ValueError):
                           logger.warning(f"Could not find content item for ID/index {cid} in the list.")

                 logger.info(f"Fetched details for {len(interacted_courses_details)} interacted courses.")

            # Pass the raw data (list or dict) to the recommendation function
            recommendations = generate_recommendations(profile_data, all_contents_raw)
            logger.info(f"Generated {len(recommendations)} recommendations for user {user['uid']} on profile page.")


        except Exception as e:
            logger.error(f"Failed to fetch profile data or related details for user {user['uid']}: {e}")
    else:
        logger.warning("Realtime Database not initialized. Cannot fetch profile data.")


    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "profile": profile_data,
        "coequipiers": coequipiers_details,
        "interacted_courses": interacted_courses_details,
        "recommendations": recommendations
    })

@app.post("/profile/update")
async def update_profile(request: Request, user=Depends(require_user), profile_data: Dict[str, Any] = Body(...)):
    """Updates user profile data in Realtime Database."""
    if rt_db:
        try:
            user_ref = rt_db.child("users").child(user['uid'])
            allowed_fields = [
                "Nom", "title", "bio", "linkedin", "website", "location",
                "Communautés", "Compétences", "Centres_d'Intérêt",
                "notify_email", "notify_push", "notify_club"
            ]
            update_data = {}

            for field in allowed_fields:
                 if field in profile_data:
                     value = profile_data[field]
                     if field in ["Communautés", "Compétences", "Centres_d'Intérêt"]:
                         if isinstance(value, str):
                             update_data[field] = [item.strip() for item in value.split(',') if item.strip()]
                         elif isinstance(value, list):
                             update_data[field] = [str(item).strip() for item in value if str(item).strip()]
                         else:
                             logger.warning(f"Unexpected data type for {field}: {type(value)}. Expected string or list.")
                             update_data[field] = []
                     elif field in ["notify_email", "notify_push", "notify_club"]:
                          update_data[field] = bool(value)
                     else:
                         update_data[field] = value


            if update_data:
                 user_ref.update(update_data)
                 logger.info(f"Profile updated for user {user['uid']}. Updated fields: {list(update_data.keys())}")
                 return JSONResponse({"status": "ok", "message": "Profile updated successfully"})
            else:
                 logger.warning(f"Profile update request for user {user['uid']} contained no allowed or changed fields.")
                 return JSONResponse({"status": "ok", "message": "No profile fields were updated."})

        except Exception as e:
            logger.error(f"Failed to update profile for user {user['uid']}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile.")
    else:
         logger.warning("Realtime Database not initialized. Cannot update profile.")
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database service unavailable.")


@app.post("/recommend")
async def create_recommendation(
    request: Request,
    title: str = Form(...),
    details: str = Form(...),
    user=Depends(require_user)
):
    """Creates a new recommendation in Realtime Database."""
    if rt_db:
        try:
            recs_ref = rt_db.child("recommendations").child(user['uid'])
            new_ref = recs_ref.push()
            new_ref.set({
                "title": title,
                "details": details,
                "created_at": admin_db.SERVER_TIMESTAMP
            })
            logger.info(f"Recommendation created for user {user['uid']} with key {new_ref.key}.")
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        except Exception as e:
            logger.error(f"Failed to create recommendation for user {user['uid']}: {e}")
            request.session["error"] = "Failed to create recommendation."
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        logger.warning("Realtime Database not initialized. Cannot create recommendation.")
        request.session["error"] = "Database service unavailable. Cannot create recommendation."
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


# --- Basic Recommendation Logic ---
def generate_recommendations(user_profile: Dict[str, Any], all_contents_raw: Any) -> List[Dict[str, Any]]:
    """Generates simple content-based recommendations based on user profile."""
    recommendations = []
    if not user_profile or all_contents_raw is None:
        return recommendations

    # Convert raw content data (list or dict) into a list of dictionaries for processing
    all_contents_list = []
    if isinstance(all_contents_raw, dict):
        # If it's a dictionary, convert values to a list and add the original key as 'id'
        all_contents_list = [{"id": cid, **c_data} for cid, c_data in all_contents_raw.items() if isinstance(c_data, dict)]
        logger.info("Recommendation function received dictionary, converted to list with IDs.")
    elif isinstance(all_contents_raw, list):
        # If it's a list, use it directly and add list index as 'id'
        all_contents_list = [{"id": index, **item} for index, item in enumerate(all_contents_raw) if isinstance(item, dict)]
        logger.info("Recommendation function received list, added index as IDs.")
    else:
        logger.warning(f"Recommendation function received unexpected content type: {type(all_contents_raw)}")
        return recommendations # Return empty list for unexpected types


    user_skills = [skill.lower() for skill in user_profile.get("Compétences", []) if isinstance(skill, str)]
    user_interests = [interest.lower() for interest in user_profile.get("Centres_d'Intérêt", []) if isinstance(interest, str)]
    # Ensure interacted course IDs are strings for consistent comparison with generated 'id'
    interacted_course_ids = [str(cid) for cid in user_profile.get("Derniers_Cours_Interagis", []) if isinstance(cid, (int, str))]

    keywords = user_skills + user_interests
    logger.info(f"Generating recommendations based on keywords: {keywords}")

    for content_item in all_contents_list:
        content_id = str(content_item.get("id")) # Get the ID (original key or list index)
        if content_id in interacted_course_ids:
            continue

        content_category = content_item.get("Category", "").lower()
        content_description = content_item.get("Description", "").lower()
        content_title = content_item.get("Title", "").lower()

        if any(keyword in content_category or keyword in content_description or keyword in content_title for keyword in keywords):
            youtube_id = extract_youtube_id(content_item.get("Link"))
            # Use the standard YouTube embed URL format
            embed_link = f"https://www.youtube.com/embed/{youtube_id}" if youtube_id else None

            recommendations.append({
                "id": content_id, # Use the captured ID
                "Title": content_item.get("Title", "Unknown Title"),
                "Category": content_item.get("Category", "Unknown Category"),
                "Description": content_item.get("Description", "No description available"),
                "Link": content_item.get("Link", "#"),
                "EmbedLink": embed_link,
                "Rating": content_item.get("Rating", 0)
            })

    sorted_recommendations = sorted(
        recommendations,
        key=lambda rec: rec.get("Rating", 0),
        reverse=True
    )

    return sorted_recommendations[:10]



# --- test ---

@app.get("/test-reco", response_class=HTMLResponse)
async def test_reco_page(request: Request, user=Depends(get_session_user)):
    """Page de test des recommandations"""
    return templates.TemplateResponse("test_reco.html", {"request": request,"user": user,})

@app.post("/test-reco", response_class=HTMLResponse)
async def process_test_reco(
    request: Request,
    student_id: str = Form(...)
):
    """Traitement du formulaire de test"""
    recommendations = []
    error = None
    
    try:
        # Vérification de l'existence de l'étudiant
        student_ref = rt_db.child("users").child(student_id)
        if not student_ref.get():
            pass

        # Appel à votre fonction Gemini
        json_response = llm.reco_llm(student_id)
        
        # Nettoyage et parsing du JSON
        cleaned_json = re.sub(r'^```json\s*|\s*```$', '', json_response, flags=re.MULTILINE)
        data = json.loads(cleaned_json.strip())
        
        # Récupération des titres recommandés
        recommended_titles = [course["Title"] for course in data.get("Cours_Recommandés", [])]
        
        # Récupération des contenus
        all_contents = rt_db.child("contents").get()
        contents = []
        
        if isinstance(all_contents, dict):
            contents = all_contents.values()
        elif isinstance(all_contents, list):
            contents = all_contents
        
        # Filtrage des recommandations
        recommendations = [
            content for content in contents 
            if isinstance(content, dict) and content.get("Title") in recommended_titles
        ]

    except Exception as e:
        error = f"Erreur : {str(e)}"
        logger.error(f"Test recommendation error: {error}", exc_info=True)

    return templates.TemplateResponse("test_reco.html", {
        "request": request,
        "recommendations": recommendations,
        "error": error,
        "student_id": student_id
    })

# --- test ---




# --- Error Handling ---
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handles 404 Not Found errors."""
    return templates.TemplateResponse("error.html", {
        "request": request,
        "message": "Page not found"
    }, status_code=status.HTTP_404_NOT_FOUND)

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: Exception):
    """Handles 500 Internal Server Errors."""
    logger.error(f"Internal Server Error: {exc}", exc_info=True)
    return templates.TemplateResponse("error.html", {
        "request": request,
        "message": "Internal server error occurred."
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
     logger.error(f"An unhandled exception occurred: {exc}", exc_info=True)
     return templates.TemplateResponse("error.html", {
         "request": request,
         "message": "An unexpected error occurred."
     }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("static"):
        os.makedirs("static")
    if not os.path.exists("templates"):
        os.makedirs("templates")
    if not os.path.exists("templates/base.html"):
        with open("templates/base.html", "w") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>{% block title %}{% endblock %}</title>\n</head>\n<body>\n{% block content %}{% endblock %}\n</body>\n</html>")
        logger.info("Created a placeholder templates/base.html")
    if not os.path.exists("templates/error.html"):
        with open("templates/error.html", "w") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Error</title>\n</head>\n<body>\n<h1>Error</h1>\n<p>{{ message }}</p>\n</body>\n</html>")
        logger.info("Created a placeholder templates/error.html")
    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
         logger.warning(f"'{SERVICE_ACCOUNT_KEY_PATH}' not found. Create this file with your Firebase service account key.")

    uvicorn.run(app, host="localhost", port=8000)
