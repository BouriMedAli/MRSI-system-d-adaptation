# MRSI System d'Adaptation

![Project Logo](assets/logo.png)

This project is a **Recommendation System** designed to provide personalized recommendations for students based on their skills, interests, and interactions. It also includes functionality for comparing machine learning models (KNN, SVD) to evaluate their performance in generating recommendations.

This branch, **Ahmedou_Yahye_branch**, contains the latest updates and features for the system.

> **Note**: This project was created by **Ahmedou Yahye** as part of a student project for **Système de Recommandation** at **FSS**, as part of a projevt on **Master's in Computer Science**, and was supervised by **PhD Mrs. Corinne Amel Zayani**.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Dataset](#dataset)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)

---

## Features

1. **Global Recommendations**: Displays top students based on the number of interactions.
2. **Personalized Recommendations**:
   - Content-based recommendations using cosine similarity.
   - Recommendations using KNN and SVD models.
3. **Model Comparison**: Compares the performance of KNN and SVD models using RMSE and MAE metrics.
4. **User Management**:
   - Add new users to the dataset.
   - Search for users by ID or name.
5. **Interactive Web Interface**: Built with FastAPI and Jinja2 templates for a user-friendly experience.

---

## Project Structure

```
├── app.py                     # Main FastAPI application
├── dataset/
│   └── dataset_etudiants.csv  # Dataset containing student information
├── modules/
│   ├── __init__.py            # Module initialization
│   ├── evaluation.py          # Model training and evaluation logic
│   ├── models.py              # Pydantic models for data validation
│   └── recommender.py         # Recommendation logic
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   └── js/
│       └── script.js          # JavaScript for interactivity
├── templates/
│   ├── base.html              # Base template for all pages
│   ├── index.html             # Home page
│   ├── compare.html           # Model comparison page
│   ├── add_user.html          # Add user form
│   ├── user_comparison.html   # User profile and recommendations
│   └── error.html             # Error page
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BouriMedAli/MRSI-system-d-adaptation.git
   cd MRSI-system-d-adaptation
   git checkout Ahmedou_Yahye_branch
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn app:app --reload --host 127.0.0.1 --port 8000
   ```

5. Open your browser and navigate to `http://127.0.0.1:8000`.

---

## Usage

### Home Page
- Displays the top students based on the number of interactions.
- Click on a student's profile to view personalized recommendations.

### Add User
- Navigate to `/add_user` to add a new student to the dataset.

### Compare Models
- Navigate to `/compare` to view the performance comparison of KNN and SVD models.

### Search
- Use the search bar to find a student by ID or name.

---

## API Endpoints

### Recommendations
- **`GET /`**: Displays global recommendations.
- **`GET /user/{user_id}`**: Displays personalized recommendations for a specific user.

### Model Comparison
- **`GET /compare`**: Compares the performance of KNN and SVD models.

### User Management
- **`GET /add_user`**: Displays the form to add a new user.
- **`POST /add_user`**: Adds a new user to the dataset.

### Search
- **`GET /search?query={query}`**: Searches for a student by ID or name.

---

## Dataset

The dataset is stored in `dataset/dataset_etudiants.csv` and contains the following columns:

- `ID_Étudiant`: Unique identifier for each student.
- `Nom`: Name of the student.
- `Travaux_Collaboratifs`: Teamwork score.
- `Coéquipiers`: List of teammates.
- `Communautés`: List of communities the student belongs to.
- `Nombre_Interactions`: Number of interactions.
- `Compétences`: List of skills.
- `Centres_d'Intérêt`: List of interests.

---

## Technologies Used

- **Backend**: FastAPI
- **Frontend**: Jinja2, TailwindCSS
- **Machine Learning**: Scikit-learn, Surprise
- **Database**: CSV-based storage
- **Other**: Pydantic for data validation

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

---continue ...---
