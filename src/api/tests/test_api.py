
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_recommend_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get(
            "/recommend/courses/5",
            params={"skills": "python", "interests": "jeux vidéo", "learning_styles": "Visuel"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "student_id" in data
        assert data["student_id"] == 5
        assert "teammates" in data
        assert isinstance(data["teammates"], list)
        assert "courses" in data
        assert isinstance(data["courses"], list)
        assert len(data["courses"]) > 0
        assert "motivational_message" in data
        assert isinstance(data["motivational_message"], str)

@pytest.mark.asyncio
async def test_student_profile_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/students/5")
        assert response.status_code == 200
        data = response.json()
        assert "ID_Étudiant" in data
        assert data["ID_Étudiant"] == 5
        assert "Nom" in data
        assert "Compétences" in data
        assert isinstance(data["Compétences"], list)
        assert "Centres_d_Intérêt" in data
        assert isinstance(data["Centres_d_Intérêt"], list)

@pytest.mark.asyncio
async def test_ai_chat_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post(
            "/ai-chat",
            json={"query": "Quels cours sont les meilleurs pour Python et les jeux vidéo ?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert isinstance(data["response"], str)
