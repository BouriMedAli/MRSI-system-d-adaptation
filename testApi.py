import requests

# URL de l'API
url = "http://127.0.0.1:8000/"

# Effectuer une requête GET
response = requests.get(url)

# Afficher la réponse
print(response.json())  # Devrait afficher {'message': 'Hello, World!'}
