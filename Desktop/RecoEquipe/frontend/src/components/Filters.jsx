import React, { useState } from 'react'; // Ajoutez cette ligne en haut
const Filters = ({ skills, interests, onFilter }) => {
    const [selectedSkills, setSelectedSkills] = useState([]);
    const [selectedInterests, setSelectedInterests] = useState([]);
  
    const handleApply = () => {
      onFilter(selectedSkills, selectedInterests);
    };
  
    return (
      <div className="filters">
        <div>
          <h3>Compétences</h3>
          <select 
            multiple
            onChange={(e) => setSelectedSkills(
              Array.from(e.target.selectedOptions, option => option.value)
            )}
          >
            {skills.map(skill => (
              <option key={skill} value={skill}>{skill}</option>
            ))}
          </select>
        </div>
        
        <div>
          <h3>Centres d'intérêt</h3>
          <select 
            multiple
            onChange={(e) => setSelectedInterests(
              Array.from(e.target.selectedOptions, option => option.value)
            )}
          >
            {interests.map(interest => (
              <option key={interest} value={interest}>{interest}</option>
            ))}
          </select>
        </div>
        
        <button onClick={handleApply}>Appliquer</button>
      </div>
    );
  };
  
  export default Filters;