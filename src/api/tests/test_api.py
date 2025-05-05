```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_recommend_endpoint():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get(
            "/recommend/courses/5",
            params={"skills": "python", "interests": "jeux vidéo", "learning_styles": "Visual"}
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
```