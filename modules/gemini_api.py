import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv 
import pandas as pd
import json
import re

load_dotenv() 

# --- Configure API Key ---
try:
    # Load the API key from the environment (now includes variables from .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    

    if not api_key:
        raise ValueError("Error: GOOGLE_API_KEY not found.\n"
                         "Please ensure it's defined in your .env file or system environment variables.")

    
    genai.configure(api_key=api_key)

except ValueError as e:
    print(e, file=sys.stderr) # Print error message to standard error
    sys.exit(1) # Exit the script with an error code

# --- Model and Prompt Setup ---
model_name = "gemini-2.0-flash"


#e = input("Enter the name of the student ou id : ")




def reco_llm(e):
    # Load the data from the CSV files
    df_etudiants = pd.read_csv("dataset/dataset_etudiants.csv")
    df_cours = pd.read_csv("dataset/cours.csv")

    # Convert the DataFrames to strings
    de = df_etudiants.to_string(index=False)
    dc = df_cours.to_string(index=False)

    # Construct the prompt text
    prompt_text = de + "\n" + dc + "\n \n recommende des cours pour l'étudiant ci-dessus"+ e +" en fonction de ses notes et de ses centres d'intérêt. \n\n" + "Recommandation : \n 1-donne sous forme dun JSON file ex:{'ID_Étudiant': ..., 'Nom': ..., 'Centres_d'Intérêt': [...], 'Cours_Recommandés': [{...}...]} \n 2-ne ajoute pas de commentaire \n 3-ne donne pas d'explication \n 4- ne repond pas par oui ou non \n 5- ne repond pas par une phrase \n 6- ne repond pas par un seul mot \n 7- ne repond pas par une liste \n 8- ne repond pas par un tableau \n 9- ne repond pas par une phrase de remerciement \n 10- ne repond pas par une phrase de politesse \n 11- ne repond pas par une phrase de salutation \n 12- ne repond pas par une phrase de conclusion \n 13- ne repond pas par une phrase de transition \n 14- ne repond pas par une phrase d'introduction \n 15- ne repond pas par une phrase de rappel \n 16- ne repond pas par une phrase de reformulation \n 17- ne repond pas par une phrase de clarification \n 18- ne repond pas par une phrase d'excuse \n 19- ne repond pas par une phrase d'alerte \n 20- ne repond pas par une phrase d'avertissement \n 21- ne repond pas par une phrase d'invitation \n 22- ne repond pa spar une phrase de suggestion \n 23- ne donne pa sde lien ou d'adresse URL ou d'adresse e-mail ou d'adresse postale ou d'adresse IP ou d'adresse MAC ou d'adresse physique ou d'adresse virtuelle ou d'adresse réseau ou d'adresse de site Web ou d'adresse de page Web ou d'adresse de profil ou d'adresse de compte ou d'adresse de service ou d'adresse de produit ou d'adresse de marque ou d'adresse de société ou d'adresse de personne physique"

    try:
        #print(f"Initializing model: {model_name}...")
        model = genai.GenerativeModel(model_name)

        #print(f"Sending prompt: '{prompt_text}'")
        response = model.generate_content(prompt_text)

        json_reco = response.text

        try:
            # Remove Markdown code block syntax using regex
            cleaned_json = re.sub(r'^```json\s*|\s*```$', '', json_reco, flags=re.MULTILINE)

            # Parse the cleaned JSON
            parsed_json = json.loads(cleaned_json.strip())

            # Convert back to formatted JSON
            formatted_json = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            return formatted_json

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print("Cleaned response:", cleaned_json)


        # Inspect other parts of the response
        # print("\n--- Safety Ratings ---")
        # print(response.prompt_feedback)

    except Exception as e:
        # Catch potential errors during API call or processing
        print(f"\nAn error occurred: {e}", file=sys.stderr)




