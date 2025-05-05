async function getRecommendation() {
    const userId = document.getElementById('userIdInput').value;
    const resultDiv = document.getElementById('result');

    if (!userId) {
        resultDiv.innerHTML = "Veuillez entrer un ID utilisateur valide.";
        return;
    }

    const response = await fetch('http://127.0.0.1:8000/recommend/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: parseInt(userId) })
    });

    if (response.ok) {
        const data = await response.json();
        resultDiv.innerHTML = `<h2>Recommandations:</h2> <p>${data.recommendations.join(", ")}</p>`;
    } else {
        resultDiv.innerHTML = "Erreur dans la récupération des recommandations.";
    }
}
