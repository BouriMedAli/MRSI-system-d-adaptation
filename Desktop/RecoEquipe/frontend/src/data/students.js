export const students = [
    {
      "ID_Étudiant": 1,
      "Nom": "Etudiant_1",
      "Travaux_Collaboratifs": 8,
      "Coéquipiers": [49, 36, 30],
      "Communautés": ["Club Robotique", "Groupe IA"],
      "Nombre_Interactions": 91,
      "Compétences": ["Blockchain", "IA", "Data Science"],
      "Centres_d_Intérêt": ["Jeux vidéo", "Musique"]
    },
    {
      "ID_Étudiant": 2,
      "Nom": "Etudiant_2",
      "Travaux_Collaboratifs": 5,
      "Coéquipiers": [16, 5],
      "Communautés": ["Club Entrepreneurs", "Groupe IA"],
      "Nombre_Interactions": 63,
      "Compétences": ["IA", "Blockchain", "Python"],
      "Centres_d_Intérêt": ["Musique"]
    }
    // ... autres étudiants
  ];
  
  // Fonction pour obtenir toutes les compétences uniques
  export const getAllSkills = () => {
    const skills = new Set();
    students.forEach(student => {
      student.Compétences.forEach(skill => skills.add(skill));
    });
    return Array.from(skills);
  };
  
  // Fonction pour obtenir tous les centres d'intérêt uniques
  export const getAllInterests = () => {
    const interests = new Set();
    students.forEach(student => {
      student.Centres_d_Intérêt.forEach(interest => interests.add(interest));
    });
    return Array.from(interests);
  };