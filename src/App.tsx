import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard.tsx';
import {BrowserRouter as Router, Routes, Route, Link} from "react-router-dom";
import CountriesPage from "./pages/CountriesPage.tsx";
import MapPage from "./pages/MapPage.tsx";
import ComparisonPage from './pages/Comparison.tsx';

const App = () => {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/countries">Countries</Link></li>
            <li><Link to="/map">World Map</Link></li>
            <li><Link to="/comparison">Comparison</Link></li>
            <li><Link to="/dashboard">Dashboard</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/countries" element={<CountriesPage/>}/>
          <Route path="/map" element={<MapPage/>}/>
          <Route path="/comparison" element={<ComparisonPage/>}/>
          <Route path="/dashboard" element={<Dashboard/>}/>
        </Routes>
      </div>
    </Router>
  
  );
}

export default App;
