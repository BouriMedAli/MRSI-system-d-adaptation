import React, { useEffect, useState } from 'react';
import Reveal from 'reveal.js';
import 'reveal.js/dist/reveal.css';
import 'reveal.js/dist/theme/black.css';
import './App.css';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {
  const [data, setData] = useState([]);
  const [stats, setStats] = useState({});

  useEffect(() => {
    // Load and parse CSV data
    fetch('/dataset_etudiants.csv')
      .then(r => r.text())
      .then(text => {
        const lines = text.split('\n').filter(l => l.trim());
        const headers = lines[0].split(',').map(h => h.trim());
        
        const allData = lines.slice(1).map(line => {
          const vals = line.split(',');
          return headers.reduce((obj, h, i) => ({ ...obj, [h]: vals[i]?.trim() }), {});
        });
        
        setData(allData);
        
        // Calculate statistics
        const totalStudents = allData.length;
        const avgCollaborations = allData.reduce((sum, s) => sum + parseInt(s.Travaux_Collaboratifs || 0), 0) / totalStudents;
        const avgInteractions = allData.reduce((sum, s) => sum + parseInt(s.Nombre_Interactions || 0), 0) / totalStudents;
        
        // Communities analysis
        const communitiesMap = {};
        allData.forEach(student => {
          const communities = student.Communautés.replace(/[\[\]']/g, '').split(',').map(c => c.trim());
          communities.forEach(comm => {
            if (comm) {
              communitiesMap[comm] = (communitiesMap[comm] || 0) + 1;
            }
          });
        });
        
        // Skills analysis
        const skillsMap = {};
        allData.forEach(student => {
          const skills = student.Compétences.replace(/[\[\]']/g, '').split(',').map(s => s.trim());
          skills.forEach(skill => {
            if (skill) {
              skillsMap[skill] = (skillsMap[skill] || 0) + 1;
            }
          });
        });
        
        // Interests analysis
        const interestsMap = {};
        allData.forEach(student => {
          const interests = student.Centres_d_Intérêt?.replace(/[\[\]']/g, '').split(',').map(i => i.trim()) || [];
          interests.forEach(interest => {
            if (interest) {
              interestsMap[interest] = (interestsMap[interest] || 0) + 1;
            }
          });
        });
        
        setStats({
          totalStudents,
          avgCollaborations: avgCollaborations.toFixed(1),
          avgInteractions: avgInteractions.toFixed(0),
          communities: Object.entries(communitiesMap).map(([name, value]) => ({ name, value })),
          skills: Object.entries(skillsMap).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value),
          interests: Object.entries(interestsMap).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
        });
      });
  }, []);

  useEffect(() => {
    if (Object.keys(stats).length > 0) {
      const deck = new Reveal({
        hash: true,
        transition: 'slide',
        backgroundTransition: 'fade'
      });
      deck.initialize();
    }
  }, [stats]);

  const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#14b8a6'];

  if (Object.keys(stats).length === 0) {
    return <div className="loading">Loading presentation...</div>;
  }

  return (
    <div className="reveal">
      <div className="slides">
        
        {/* Slide 1: Title */}
        <section data-background-gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
          <h1 className="title-main">Student Analytics</h1>
          <h3 className="subtitle">Comprehensive Analysis of Student Collaboration & Engagement</h3>
          <p className="date-text">Data-Driven Insights • 2024</p>
        </section>

        {/* Slide 2: Overview */}
        <section data-background-gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
          <h2>Overview</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{stats.totalStudents}</div>
              <div className="stat-label">Total Students</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.avgCollaborations}</div>
              <div className="stat-label">Avg Collaborations</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.avgInteractions}</div>
              <div className="stat-label">Avg Interactions</div>
            </div>
          </div>
        </section>

        {/* Slide 3: Communities */}
        <section data-background-gradient="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
          <h2>Student Communities</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={stats.communities}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#fff" angle={-45} textAnchor="end" height={120} />
                <YAxis stroke="#fff" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Slide 4: Skills Distribution */}
        <section data-background-gradient="linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
          <h2>Top Skills</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={stats.skills.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis type="number" stroke="#fff" />
                <YAxis dataKey="name" type="category" stroke="#fff" width={120} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="value" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Slide 5: Skills Pie Chart */}
        <section data-background-gradient="linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)">
          <h2>Skills Distribution</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={450}>
              <PieChart>
                <Pie
                  data={stats.skills.slice(0, 8)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stats.skills.slice(0, 8).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Slide 6: Interests */}
        <section data-background-gradient="linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)">
          <h2>Student Interests</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={stats.interests}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#333" angle={-45} textAnchor="end" height={120} />
                <YAxis stroke="#333" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="value" fill="#10b981" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Slide 7: Collaboration Insights */}
        <section data-background-gradient="linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)">
          <h2>Key Insights</h2>
          <div className="insights-container">
            <div className="insight-box">
              <h3>🤝 Collaboration</h3>
              <p>Students average <strong>{stats.avgCollaborations}</strong> collaborative projects</p>
            </div>
            <div className="insight-box">
              <h3>💬 Engagement</h3>
              <p>Average of <strong>{stats.avgInteractions}</strong> interactions per student</p>
            </div>
            <div className="insight-box">
              <h3>🎯 Communities</h3>
              <p><strong>{stats.communities.length}</strong> active student communities</p>
            </div>
            <div className="insight-box">
              <h3>⚡ Skills</h3>
              <p><strong>{stats.skills.length}</strong> different skills identified</p>
            </div>
          </div>
        </section>

        {/* Slide 8: Conclusion */}
        <section data-background-gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
          <h2>Conclusion</h2>
          <div className="conclusion-content">
            <p className="conclusion-text">
              Our student community demonstrates strong engagement across multiple domains:
            </p>
            <ul className="conclusion-list">
              <li>✓ Diverse skill sets spanning technology and design</li>
              <li>✓ Active participation in collaborative projects</li>
              <li>✓ Strong community involvement and networking</li>
              <li>✓ Balanced interests across various activities</li>
            </ul>
            <p className="conclusion-footer">
              <strong>Thank you!</strong>
            </p>
          </div>
        </section>

      </div>
    </div>
  );
}

export default App;
