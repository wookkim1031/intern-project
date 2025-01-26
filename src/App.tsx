import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard.tsx';
import {BrowserRouter as Router, Routes, Route, Link} from "react-router-dom";
import CountriesPage from "./pages/CountriesPage.tsx";
import MapPage from "./pages/MapPage.tsx";
import ComparisonPage from './pages/Comparison.tsx';
import AdvancedMetricsPage from "./pages/AdvancedMetrics.tsx";
import Products from './pages/Product.tsx';

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
            <li><Link to="/advanced_metrics">Advanced metrics</Link></li>
            <li><Link to="/products">Products</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/countries" element={<CountriesPage/>}/>
          <Route path="/map" element={<MapPage/>}/>
          <Route path="/comparison" element={<ComparisonPage/>}/>
          <Route path="/advanced_metrics" element={<AdvancedMetricsPage/>}/>
          <Route path="/dashboard" element={<Dashboard/>}/>
          <Route path="/products" element={<Products/>}/>
        </Routes>
      </div>
    </Router>
  
  );
}

export default App;
