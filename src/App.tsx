import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard.tsx';
import {BrowserRouter as Router, Routes, Route, Link} from "react-router-dom";
import CountriesPage from "./pages/CountriesPage.tsx";
import MapPage from "./pages/MapPage.tsx";
import TimeIntervalPage from "./pages/TimeIntervalPage.tsx";

const App = () => {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/countries">Countries</Link></li>
            <li><Link to="/map">World Map</Link></li>
            <li><Link to="/time-interval">Time Intervals</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/countries" element={<CountriesPage/>}/>
          <Route path="/map" element={<CountriesPage/>}/>
          <Route path="/time-interval" element={<TimeIntervalPage/>}></Route>
        </Routes>
      </div>
    </Router>
  
  );
}

export default App;
