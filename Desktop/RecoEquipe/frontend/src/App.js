import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';  // Chemin corrigé
import Home from './pages/Home';          // Chemin corrigé
import Students from './pages/Students';  // Chemin corrigé
import Teams from './pages/Teams';        // Chemin corrigé
import './App.css';

function App() {
  return (
    <Router>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/students" element={<Students />} />
          <Route path="/teams" element={<Teams />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;