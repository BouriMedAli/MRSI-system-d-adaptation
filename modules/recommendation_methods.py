import firebase_admin
from firebase_admin import db as admin_db
import logging
from typing import List, Dict, Any, Optional
from sklearn.neighbors import NearestNeighbors # Using scikit-learn for KNN
import numpy as np
import google.generativeai as genai # Import Generative AI library
import os # Needed for environment variables if not configured globally
import json # For parsing LLM response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Realtime Database instance safely
# Assumes Firebase Admin SDK is initialized in the main application (main.py)
rt_db = None
try:
    rt_db = admin_db.reference('/')
    logger.info("Firebase RTDB reference obtained in recommendation_methods.")
except NameError:
    logger.error("Firebase Admin SDK not initialized, rt_db is not available in recommendation_methods.")
    rt_db = None # Set to None if initialization failed
except Exception as e:
     logger.error(f"Error getting RTDB reference in recommendation_methods: {e}")
     rt_db = None


# Configure Generative AI (assuming API key is set in .env and loaded by main.py)
# It's best practice to configure this once at application startup in main.py
# but we'll add a check here for robustness if this module is used standalone.
try:
    if not genai.configured:
         api_key = os.getenv("GOOGLE_API_KEY")
         if not api_key:
              logger.error("GOOGLE_API_KEY not found. LLM recommendations will not work.")
         else:
              genai.configure(api_key=api_key)
              logger.info("Generative AI configured in recommendation_methods.")
except Exception as e:
    logger.error(f"Failed to configure Generative AI in recommendation_methods: {e}")


def get_all_users_for_recommendation() -> Dict[str, Dict[str, Any]]:
    """Fetches all user data from Firebase Realtime DB for recommendation."""
    if rt_db:
        try:
            users_data = rt_db.child("users").get()
            if isinstance(users_data, dict):
                 logger.info(f"Fetched {len(users_data)} users for recommendation.")
                 return users_data
            elif users_data is None:
                 logger.info("No users found for recommendation.")
                 return {}
            else:
                 logger.warning(f"Firebase /users node returned unexpected type for recommendation: {type(users_data)}. Expected dict.")
                 return {} # Return empty dict for unexpected types
        except Exception as e:
            logger.error(f"Failed to fetch users for recommendation: {e}")
            return {}
    else:
        logger.warning("Realtime Database not initialized. Cannot fetch users for recommendation.")
        return {}

def get_all_contents_for_recommendation() -> Any:
    """Fetches all content data from Firebase Realtime DB."""
    if rt_db:
        try:
            contents_data = rt_db.child("contents").get()
            logger.info(f"Fetched content data for recommendation. Type: {type(contents_data)}")
            return contents_data # Return raw data (list or dict)
        except Exception as e:
            logger.error(f"Failed to fetch contents for recommendation: {e}")
            return None
    else:
        logger.warning("Realtime Database not initialized. Cannot fetch contents for recommendation.")
        return None


def vectorize_user_profile(user_profile: Dict[str, Any], all_possible_terms: List[str]) -> np.ndarray:
    """Converts user profile (skills, interests, communities) into a feature vector."""
    vector = np.zeros(len(all_possible_terms))
    profile_terms = []
    # Combine relevant list fields into a single list of terms
    profile_terms.extend([str(item).lower() for item in user_profile.get("Compétences", []) if isinstance(item, (str, int, float))])
    profile_terms.extend([str(item).lower() for item in user_profile.get("Centres_d'Intérêt", []) if isinstance(item, (str, int, float))])
    profile_terms.extend([str(item).lower() for item in user_profile.get("Communautés", []) if isinstance(item, (str, int, float))])

    for term in profile_terms:
        try:
            # Find the index of the term in the predefined list and set the vector value to 1
            index = all_possible_terms.index(term)
            vector[index] = 1
        except ValueError:
            # Term not in the predefined list, ignore or log
            pass # logger.debug(f"Term '{term}' not in all_possible_terms.")

    return vector

def KNN_similarity(current_user_id: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
    """
    Recommends users based on K-Nearest Neighbors similarity using profile data.
    This is a simple example using skills, interests, and communities.
    """
    logger.info(f"Generating KNN recommendations for user {current_user_id}")
    all_users_data = get_all_users_for_recommendation()

    if not all_users_data:
        return []

    # Exclude the current user from the list
    other_users_data = {uid: data for uid, data in all_users_data.items() if uid != current_user_id}

    if not other_users_data:
        logger.info("No other users available for KNN recommendation.")
        return []

    current_user_profile = all_users_data.get(current_user_id)
    if not current_user_profile:
        logger.warning(f"Profile not found for current user {current_user_id}. Cannot generate KNN recommendations.")
        return []

    # 1. Collect all unique terms (skills, interests, communities) from all users
    all_terms = set()
    for user_data in all_users_data.values():
         all_terms.update([str(item).lower() for item in user_data.get("Compétences", []) if isinstance(item, (str, int, float))])
         all_terms.update([str(item).lower() for item in user_data.get("Centres_d'Intérêt", []) if isinstance(item, (str, int, float))])
         all_terms.update([str(item).lower() for item in user_data.get("Communautés", []) if isinstance(item, (str, int, float))])

    all_possible_terms = sorted(list(all_terms)) # Sort for consistent vector indexing
    logger.info(f"Collected {len(all_possible_terms)} unique terms across all users for KNN.")

    if not all_possible_terms:
         logger.warning("No terms found across all users. Cannot vectorize profiles for KNN.")
         return []

    # 2. Vectorize all user profiles
    user_vectors = {}
    for uid, user_data in all_users_data.items():
        user_vectors[uid] = vectorize_user_profile(user_data, all_possible_terms)

    current_user_vector = user_vectors.get(current_user_id)
    if current_user_vector is None:
         logger.error(f"Failed to vectorize current user profile {current_user_id} for KNN.")
         return []

    # Prepare data for KNN
    other_user_ids = list(other_users_data.keys())
    other_user_vectors = np.array([user_vectors[uid] for uid in other_user_ids])

    if len(other_user_vectors) < num_recommendations:
         logger.warning(f"Fewer than {num_recommendations} other users available for KNN. Recommending all {len(other_user_vectors)}.")
         k_neighbors = len(other_user_vectors) # Adjust k if fewer users exist
    else:
         k_neighbors = num_recommendations # Use num_recommendations as k


    # 3. Apply KNN
    # We need at least 1 neighbor to train, and k must be <= number of samples
    if k_neighbors < 1 or len(other_user_vectors) == 0:
         logger.info("Not enough users to perform KNN.")
         return []

    try:
        # Use cosine similarity as metric for sparse binary vectors
        nn = NearestNeighbors(n_neighbors=k_neighbors, metric='cosine')
        nn.fit(other_user_vectors)

        # Find the k nearest neighbors to the current user's vector
        # Reshape current_user_vector if it's a single sample
        distances, indices = nn.kneighbors([current_user_vector.reshape(1, -1)])


        # 4. Get recommended user IDs based on indices
        # Ensure indices is not empty
        if indices.size == 0:
             logger.info("KNN found no neighbors.")
             return []

        recommended_user_indices = indices[0]
        recommended_user_ids = [other_user_ids[i] for i in recommended_user_indices]

        # 5. Fetch details for recommended users
        recommended_users_details = []
        for uid in recommended_user_ids:
             user_detail = all_users_data.get(uid) # Get details from the already fetched data
             if user_detail:
                  recommended_users_details.append({
                       "ID_Étudiant": uid, # Use the user ID as the identifier
                       "Nom": user_detail.get("name", f"User {uid}"),
                       "Bio": user_detail.get("bio", "No bio available."),
                       "Skills": user_detail.get("Compétences", []),
                       "Interests": user_detail.get("Centres_d'Intérêt", []),
                       "Communities": user_detail.get("Communautés", []),
                       "Photo_URL": user_detail.get("photo_url", "/static/default-avatar.png")
                  })
        logger.info(f"Generated {len(recommended_users_details)} KNN recommendations.")
        return recommended_users_details

    except Exception as e:
        logger.error(f"Error during KNN similarity calculation: {e}")
        return []


def llm_recomand(current_user_id: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
    """
    Generates user recommendations based on LLM analysis of user profiles.
    """
    logger.info(f"Generating LLM recommendations for user {current_user_id}")

    if not genai.configured:
         logger.error("Generative AI is not configured. Cannot run LLM recommendation.")
         return []

    all_users_data = get_all_users_for_recommendation()
    # We don't necessarily need all content data for user recommendations,
    # but fetching it here is consistent with the user's original approach.
    # all_contents_raw = get_all_contents_for_recommendation() # Uncomment if needed for a more complex prompt

    if not all_users_data:
        logger.warning("No user data available for LLM recommendation.")
        return []

    current_user_profile = all_users_data.get(current_user_id)
    if not current_user_profile:
        logger.warning(f"Profile not found for current user {current_user_id}. Cannot generate LLM recommendations.")
        return []

    # Exclude the current user from the list for the LLM to consider others
    other_users_data = {uid: data for uid, data in all_users_data.items() if uid != current_user_id}

    if not other_users_data:
        logger.info("No other users available for LLM recommendation.")
        return []

    # --- Construct the Prompt for the LLM ---
    model_name = "gemini-1.5-flash-latest" # Using a more capable model for text analysis

    prompt_parts = []

    prompt_parts.append("Analyze the following user profiles and recommend users who are most similar to the target user.")
    prompt_parts.append("\n\n## All User Profiles:\n")

    # Add all user profiles (excluding the current user) to the prompt
    for uid, data in other_users_data.items():
        prompt_parts.append(f"User ID: {uid}")
        prompt_parts.append(f"Name: {data.get('name', 'N/A')}")
        prompt_parts.append(f"Bio: {data.get('bio', 'N/A')}")
        prompt_parts.append(f"Skills: {', '.join(map(str, data.get('Compétences', [])))}")
        prompt_parts.append(f"Interests: {', '.join(map(str, data.get('Centres_d\'Intérêt', [])))}")
        prompt_parts.append(f"Communities: {', '.join(map(str, data.get('Communautés', [])))}")
        # Add other relevant fields if necessary
        prompt_parts.append("---\n") # Separator between users

    prompt_parts.append("\n## Target User Profile:\n")
    prompt_parts.append(f"User ID: {current_user_id}")
    prompt_parts.append(f"Name: {current_user_profile.get('name', 'N/A')}")
    prompt_parts.append(f"Bio: {current_user_profile.get('bio', 'N/A')}")
    prompt_parts.append(f"Skills: {', '.join(map(str, current_user_profile.get('Compétences', [])))}")
    prompt_parts.append(f"Interests: {', '.join(map(str, current_user_profile.get('Centres_d\'Intérêt', [])))}")
    prompt_parts.append(f"Communities: {', '.join(map(str, current_user_profile.get('Communautés', [])))}")
    prompt_parts.append("---\n")

    prompt_parts.append(f"\nBased on the profiles provided, recommend the top {num_recommendations} users who are most similar to the target user ({current_user_id}) in terms of skills, interests, and communities.")
    prompt_parts.append("\nRespond ONLY with a JSON object. The JSON object should have a single key 'recommended_users' which contains a list of recommended user objects.")
    prompt_parts.append("Each user object in the list should include the following keys: 'ID_Étudiant', 'Nom', 'Bio', 'Compétences', 'Centres_d\'Intérêt', 'Communautés', and 'Photo_URL'.")
    prompt_parts.append("Do not include any other text, comments, or explanations outside the JSON object.")
    prompt_parts.append("Ensure the JSON is valid and can be parsed directly.")

    # Add user's negative constraints
    prompt_parts.append("\nConstraints: Do not respond with comments, explanations, single words, phrases, lists, tables, or any form of salutation, conclusion, transition, introduction, reminder, reformulation, clarification, excuse, alert, warning, invitation, suggestion, encouragement. Do not provide links or addresses (URL, email, postal, IP, MAC, physical, virtual, network, website, webpage, profile, account, service, product, brand, company, person).")


    full_prompt = "".join(prompt_parts)
    logger.info(f"Constructed LLM prompt for user {current_user_id}. (Truncated for log)")
    # logger.debug(f"Full LLM prompt: {full_prompt}") # Uncomment for debugging full prompt

    # --- Send Prompt to LLM and Parse Response ---
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(full_prompt)

        # Check for safety issues or blocked content
        if not response._result.candidates:
             logger.warning(f"LLM response was blocked or empty for user {current_user_id}. Prompt feedback: {response.prompt_feedback}")
             return []

        response_text = response.text.strip()
        logger.info(f"Received LLM response (truncated): {response_text[:200]}...")

        # Attempt to parse the JSON response
        # The LLM might sometimes include markdown code blocks, try to clean that.
        if response_text.startswith("```json") and response_text.endswith("```"):
            json_string = response_text[7:-3].strip()
        else:
            json_string = response_text

        recommended_users_data = json.loads(json_string)

        # Validate the parsed JSON structure
        if not isinstance(recommended_users_data, dict) or 'recommended_users' not in recommended_users_data or not isinstance(recommended_users_data['recommended_users'], list):
             logger.error(f"LLM response JSON has unexpected structure for user {current_user_id}: {response_text}")
             return []

        recommended_users_list = recommended_users_data['recommended_users']

        # Format the extracted user data to match the expected output format
        formatted_recommendations = []
        for user_data in recommended_users_list:
             # Ensure required fields exist, providing defaults
             formatted_recommendations.append({
                  "ID_Étudiant": str(user_data.get("ID_Étudiant", "N/A")), # Ensure ID is string
                  "Nom": user_data.get("Nom", "Unknown User"),
                  "Bio": user_data.get("Bio", "No bio available."),
                  "Skills": user_data.get("Compétences", []),
                  "Interests": user_data.get("Centres_d'Intérêt", []),
                  "Communities": user_data.get("Communautés", []),
                  "Photo_URL": user_data.get("Photo_URL", "/static/default-avatar.png") # Use default if not provided
             })

        logger.info(f"Generated {len(formatted_recommendations)} LLM recommendations.")
        return formatted_recommendations

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response JSON for user {current_user_id}: {e}\nResponse text: {response_text}")
        return []
    except Exception as e:
        logger.error(f"Error during LLM recommendation generation for user {current_user_id}: {e}")
        return []


# Dictionary to map method names to functions
USER_RECOMMENDATION_METHODS = {
    "knn": KNN_similarity,
    "llm": llm_recomand, # Renamed to 'llm'
}

# --- Basic Content Recommendation Logic (Moved from main.py) ---
# This function is used by the homepage and potentially the profile page
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
        logger.info("Content recommendation function received dictionary, converted to list with IDs.")
    elif isinstance(all_contents_raw, list):
        # If it's a list, use it directly and add list index as 'id'
        all_contents_list = [{"id": index, **item} for index, item in enumerate(all_contents_raw) if isinstance(item, dict)]
        logger.info("Content recommendation function received list, added index as IDs.")
    else:
        logger.warning(f"Content recommendation function received unexpected content type: {type(all_contents_raw)}")
        return recommendations # Return empty list for unexpected types


    user_skills = [skill.lower() for skill in user_profile.get("Compétences", []) if isinstance(skill, str)]
    user_interests = [interest.lower() for interest in user_profile.get("Centres_d'Intérêt", []) if isinstance(item, (str, int, float))] # Fixed typo
    interacted_course_ids = [str(cid) for cid in user_profile.get("Derniers_Cours_Interagis", []) if isinstance(cid, (int, str))]

    keywords = user_skills + user_interests
    logger.info(f"Generating content recommendations based on keywords: {keywords}")

    for content_item in all_contents_list:
        content_id = str(content_item.get("id")) # Get the ID (original key or list index)
        if content_id in interacted_course_ids:
            continue

        content_category = content_item.get("Category", "").lower()
        content_description = content_item.get("Description", "").lower()
        content_title = content_item.get("Title", "").lower()

        if any(keyword in content_category or keyword in content_description or keyword in content_title for keyword in keywords):
            youtube_id = extract_youtube_id(content_item.get("Link"))
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
