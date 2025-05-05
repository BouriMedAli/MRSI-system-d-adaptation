import { useState } from 'react';

const StudentCard = ({ student }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="student-card" onClick={() => setExpanded(!expanded)}>
      <h3>{student.Nom}</h3>
      <p>Interactions: {student.Nombre_Interactions}</p>
      
      {expanded && (
        <div className="details">
          <h4>Compétences:</h4>
          <div>
            {student.Compétences.map((skill, i) => (
              <span key={i} className="skill">{skill}</span>
            ))}
          </div>
          
          <h4>Intérêts:</h4>
          <div>
            {student.Centres_d_Intérêt.map((interest, i) => (
              <span key={i} className="interest">{interest}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentCard;