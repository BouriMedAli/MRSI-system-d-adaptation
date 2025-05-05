import { useState } from 'react';
import { students, getAllSkills, getAllInterests } from '../data/students';
import StudentCard from '../components/StudentCard';
import Filters from '../components/Filters';

const StudentsPage = () => {
  const [filteredStudents, setFilteredStudents] = useState(students);
  
  const handleFilter = (selectedSkills, selectedInterests) => {
    const filtered = students.filter(student => {
      const hasSkills = selectedSkills.length === 0 || 
        selectedSkills.some(skill => student.Compétences.includes(skill));
      const hasInterests = selectedInterests.length === 0 || 
        selectedInterests.some(interest => student.Centres_d_Intérêt.includes(interest));
      return hasSkills && hasInterests;
    });
    setFilteredStudents(filtered);
  };

  return (
    <div className="students-page">
      <h1>Liste des Étudiants</h1>
      <Filters 
        skills={getAllSkills()} 
        interests={getAllInterests()} 
        onFilter={handleFilter} 
      />
      <div className="students-grid">
        {filteredStudents.map(student => (
          <StudentCard key={student.ID_Étudiant} student={student} />
        ))}
      </div>
    </div>
  );
};

export default StudentsPage;