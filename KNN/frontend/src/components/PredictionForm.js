import React, { useState } from "react";
import axios from "axios";

const PredictionForm = () => {
  const [features, setFeatures] = useState("");
  const [prediction, setPrediction] = useState(null);

  const handlePredict = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/predict", {
        features: features.split(",").map(Number),
      });
      setPrediction(response.data.prediction);
    } catch (error) {
      console.error("Erreur de prédiction :", error);
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-xl font-bold mb-4">Prédiction avec KNN</h2>
      <input
        type="text"
        placeholder="Ex: 5.1,3.5,1.4,0.2"
        className="w-full p-2 border border-gray-300 rounded"
        value={features}
        onChange={(e) => setFeatures(e.target.value)}
      />
      <button
        onClick={handlePredict}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Prédire
      </button>
      {prediction !== null && (
        <p className="mt-4 text-lg font-bold">Résultat : {prediction}</p>
      )}
    </div>
  );
};

export default PredictionForm;
