# Student Recommendation System

A personalized recommendation system using Interest-Competence Graph Neural Network approach to recommend potential collaborators for students based on their interests, skills, social connections, and community involvement.

## 📋 Overview

This project implements a novel approach to student recommendations using graph theory and natural language understanding. The system analyzes multiple dimensions of student data:

- **Social connections**: Existing collaborations and network proximity
- **Interests**: Matching students with similar interests
- **Skills**: Finding complementary skill sets
- **Communities**: Identifying shared communities and groups
- **Collaboration style**: Analyzing work patterns and preferences

The system is built as a microservice architecture with a FastAPI backend and Streamlit frontend, containerized with Docker for easy deployment.

## 🧠 The Innovation: Interest-Competence Graph Neural Network

Unlike traditional recommendation systems that rely solely on matrix factorization or collaborative filtering, our approach constructs a knowledge graph that:

1. Represents students as nodes with attributes (skills, interests, collaboration scores)
2. Creates edges based on existing collaborations, community memberships, and shared interests
3. Augments this graph with centrality measures and clustering coefficients
4. Generates embeddings combining graph structure and node attributes
5. Uses these embeddings to compute multi-dimensional similarity scores

This approach allows for more nuanced recommendations that consider both direct connections and broader structural patterns in the student network.

## 🏗️ Architecture

The system consists of two main components:

### Backend API (FastAPI)

- Provides RESTful endpoints for accessing student data and recommendations
- Implements the graph-based recommendation algorithm
- Processes and analyzes the student dataset

### Frontend (Streamlit)

- User-friendly interface for interacting with the recommendation system
- Visual representation of recommendations with explanation
- Network visualization to show relationships between students

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/student-recommendation-system.git
   cd student-recommendation-system
   ```

2. Build and run the containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:8501
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔍 API Endpoints

- `GET /students` - Get a list of all students
- `GET /students/{student_id}` - Get detailed information about a specific student
- `GET /recommendations/{student_id}` - Get personalized recommendations for a student

## 📊 Features

- **Personalized Recommendations**: Get tailored recommendations for each student
- **Explanation Engine**: Understand why recommendations were made
- **Interactive Visualization**: Explore the student network visually
- **Detailed Student Profiles**: View comprehensive information about each student
- **Adjustable Parameters**: Configure the number of recommendations and other settings

## 🛠️ Technical Implementation

### Recommendation Algorithm

The recommendation system uses a multi-step process:

1. **Graph Construction**: Build a knowledge graph representing student relationships
2. **Feature Extraction**: Create matrices for interests, competencies, and communities
3. **Embedding Generation**: Combine graph structure and attribute information
4. **Similarity Calculation**: Compute multi-dimensional similarity scores
5. **Recommendation Generation**: Rank potential collaborators and provide explanations

### Containerization

The application is containerized using Docker with separate containers for:
- API service
- Streamlit frontend

### CI/CD Pipeline

The project uses GitHub Actions for:
- Automated testing
- Building and pushing Docker images to DockerHub
- Deploying to production servers

## 🔧 Configuration

Environment variables:
- `DATA_PATH`: Path to the dataset file
- `API_URL`: URL for the API service
- `PORT`: Port for the API service

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

If you have any questions or feedback, please reach out to [your-email@example.com](mailto:your-email@example.com).