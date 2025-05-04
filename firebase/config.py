import os

import firebase_admin





cred = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(cred)
print(firebase_admin.initialize_app(cred))