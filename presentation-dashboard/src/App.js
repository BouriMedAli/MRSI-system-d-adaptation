import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Papa from 'papaparse';

function App() {
  const [data, setData] = useState([]);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Charger le CSV
    fetch('/dataset_etudiants.csv')
      .then(response => response.text())
      .then(text => {
        Papa.parse(text, {
          header: true,
          complete: (results) => {
            setData(results.data.filter(row => row.ID_Étudiant));
          }
        });
      });

    // Charger l'analyse JSON
    fetch('/analysis_results.json')
      .then(response => response.json())
      .then(json => {
        setAnalysisData(json);
        setLoading(false);
      });
  }, []);

  const communityData = useMemo(() => {
    if (!analysisData) return [];
    return Object.entries(analysisData.communautes).map(([name, value]) => ({
      name,
      value
    }));
  }, [analysisData]);

  const skillsData = useMemo(() => {
    if (!analysisData) return [];
    return Object.entries(analysisData.competences).slice(0, 8).map(([name, value]) => ({
      name,
      value
    }));
  }, [analysisData]);

  const interestsData = useMemo(() => {
    if (!analysisData) return [];
    return Object.entries(analysisData.centres_interet).slice(0, 8).map(([name, value]) => ({
      name,
      value
    }));
  }, [analysisData]);

  const travauxDistribution = useMemo(() => {
    if (!analysisData) return [];
    return Object.entries(analysisData.travaux_distribution).map(([nb, count]) => ({
      nombre: `${nb} projets`,
      etudiants: count
    }));
  }, [analysisData]);

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#6366f1'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-2xl font-bold text-blue-600">Chargement des données...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      {/* En-tête */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-2xl shadow-xl p-8 border-t-4 border-blue-600">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📊 Analyse des Étudiants - Dashboard Professionnel
          </h1>
          <p className="text-gray-600 text-lg">
            Vue d'ensemble complète des activités collaboratives et compétences
          </p>
        </div>
      </div>

      {/* Cartes de statistiques */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-3xl mb-2">👥</div>
          <div className="text-3xl font-bold">{analysisData.total_etudiants}</div>
          <div className="text-blue-100 text-sm">Étudiants Total</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-3xl mb-2">🤝</div>
          <div className="text-3xl font-bold">{analysisData.travaux_collaboratifs.moyenne.toFixed(1)}</div>
          <div className="text-purple-100 text-sm">Moy. Travaux Collaboratifs</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-3xl mb-2">💬</div>
          <div className="text-3xl font-bold">{analysisData.interactions.moyenne.toFixed(0)}</div>
          <div className="text-green-100 text-sm">Moy. Interactions</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-3xl mb-2">🔗</div>
          <div className="text-3xl font-bold">{analysisData.reseau.moyenne_coequipiers}</div>
          <div className="text-orange-100 text-sm">Moy. Coéquipiers</div>
        </div>
      </div>

      {/* Graphiques principaux */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Distribution des communautés */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🏛️ Distribution des Communautés</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={communityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {communityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Compétences principales */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">💡 Compétences Principales</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={skillsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" angle={-45} textAnchor="end" height={100} />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Centres d'intérêt */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🎯 Centres d'Intérêt</h2>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={interestsData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" stroke="#6b7280" />
              <YAxis dataKey="name" type="category" stroke="#6b7280" width={120} />
              <Tooltip />
              <Bar dataKey="value" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribution des travaux collaboratifs */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">📈 Distribution Travaux Collaboratifs</h2>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={travauxDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="nombre" stroke="#6b7280" angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="etudiants" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top étudiants */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🏆 Top 10 Étudiants par Interactions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {analysisData.top_etudiants.map((student, index) => (
              <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border-l-4 border-blue-500">
                <div className="text-2xl font-bold text-blue-600">#{index + 1}</div>
                <div className="text-gray-800 font-semibold">{student.Nom}</div>
                <div className="text-gray-600 text-sm">{student.Nombre_Interactions} interactions</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-8 text-center text-gray-600">
        <p className="text-sm">Dashboard généré automatiquement • Données complètes de {analysisData.total_etudiants} étudiants</p>
      </div>
    </div>
  );
}

export default App;
