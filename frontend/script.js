document.getElementById("form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const competences = Array.from(document.getElementById("competences").selectedOptions).map(opt => opt.value);
  const interets = Array.from(document.getElementById("interets").selectedOptions).map(opt => opt.value);
  const travaux = parseInt(document.getElementById("travaux").value);

  const data = {
    competences,
    interets,
    travaux
  };

  try {
    const response = await fetch("http://127.0.0.1:8000/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    alert("Erreur: " + error.message);
    console.error(error);
  }
});

function displayResults(data) {
  const tbody = document.querySelector("#result-table tbody");
  tbody.innerHTML = "";

  const labels = [];
  const values = [];

  data.forEach(item => {
    const row = tbody.insertRow();
    row.insertCell(0).textContent = item.nom;

    const compTd = row.insertCell(1);
    item.competences.split(",").forEach(c => {
      const span = document.createElement("span");
      span.className = "ribbon";
      span.textContent = c.trim();
      compTd.appendChild(span);
    });

    const intTd = row.insertCell(2);
    item.interets.split(",").forEach(i => {
      const span = document.createElement("span");
      span.className = "ribbon";
      span.textContent = i.trim();
      intTd.appendChild(span);
    });

    labels.push(item.nom);
    values.push(item.similarity);
  });

  const ctxPie = document.getElementById("pie-chart").getContext("2d");
  new Chart(ctxPie, {
    type: "pie",
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ffb3e6", "#b3ffff", "#c2f0c2", "#ffdb4d", "#d1b3ff", "#80ffbf"]
      }]
    }
  });

  const ctxScatter = document.getElementById("scatter-chart").getContext("2d");
  new Chart(ctxScatter, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Similarité",
        data: values.map((v, i) => ({ x: i + 1, y: v })),
        backgroundColor: "#0077cc"
      }]
    },
    options: {
      scales: {
        x: { title: { display: true, text: "Étudiants" } },
        y: { title: { display: true, text: "Similarité (%)" }, min: 0, max: 100 }
      }
    }
  });
}
