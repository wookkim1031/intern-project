import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";

type PlotlyChartData = {
  data: any[];
  layout: Record<string, any>;
};

const ComparisonPage = () => {
  const [country1, setCountry1] = useState("");
  const [country2, setCountry2] = useState("");
  const [loading, setLoading] = useState<boolean>(true);
  const [chartData, ] = useState<PlotlyChartData | null>(null);
  const [countries, setCountries] = useState<string[]>([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/countries")
      .then((response) => {
          setCountry1(response.data.countries[0]);
          setCountry2(response.data.countries[1]);
          setCountries(response.data.countries)})
      .catch((error) => console.error("Error fetching time interval data:", error));
  }, []);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/comparison/${country1}/${country2}").
      then((response) => {
        
      }
  })

  const handleCountry1Change = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCountry1(e.target.value);
  } 

  const handleCountry2Change = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCountry2(e.target.value);
  } 
  return (
    <div>
      <h1>Comparison Page</h1>
      <div>
        <label htmlFor="country1">Select Country 1: </label>
        <select onChange={handleCountry1Change} id="country1DropDown" value={country1}>
          {countries.length > 0 ? (
            countries.map((country) => 
              <option value={country}>{country}</option>
            ) 
          ) : (
            <option disabled>No countries available</option>
          )}
        </select>
      </div>
      <div>
        <label htmlFor="country2">Select Country 2: </label>
        <select onChange={handleCountry2Change} id="country2DropDown" value={country2}>
          {countries.length > 0 ? (
            countries.map((country) => 
              <option value={country}>{country}</option>
            ) 
          ) : (
            <option disabled>No countries available</option>
          )}
        </select>
      </div>
    </div>
  );
};

export default ComparisonPage;