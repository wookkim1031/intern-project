import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";

type PlotlyChartData = {
  data: any[];
  layout: Record<string, any>;
};

const ComparisonPage = () => {
  const [country1, setCountry1] = useState("all");
  const [country2, setCountry2] = useState("Germany");
  const [loading, setLoading] = useState<boolean>(true);
  const [bar1Chart, setBar1Chart] = useState<PlotlyChartData | null>(null);
  const [bar2Chart, setBar2Chart] = useState<PlotlyChartData | null>(null);
  const [lineChart, setLineChart] = useState<PlotlyChartData | null>(null);
  const [countries, setCountries] = useState<string[]>([]);

  useEffect(() => {
    axios.get("https://intern-project-liart.vercel.app/countries")
      .then((response) => {
          setCountries(response.data.countries)})
      .catch((error) => console.error("Error fetching time interval data:", error));
  }, []);


  useEffect(() => {
    axios.get(`https://intern-project-liart.vercel.app/comparison/${country1}/${country2}`).
      then((response) => {
        setBar1Chart(response.data.bar_1_chart);
        setBar2Chart(response.data.bar_2_chart);
        setLineChart(response.data.line_sales_chart);})        
      .catch((error) => console.error("Error fetching comparison data:", error));
  },[country1, country2]); 

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
          <option value="all">All Products</option>
          {countries.length > 0 ? (
            countries.map((country) => (
              <option key={country} value={country}>{country}</option>
            ))
          ) : (
            <option disabled>No countries available</option>
          )}
        </select>
      </div>
      <div>
        <label htmlFor="country2">Select Country 2: </label>
          <select onChange={handleCountry2Change} id="country2DropDown" value={country2}>
          <option value="all">All Products</option>
          {countries.length > 0 ? (
            countries.map((country) => (
              <option key={country} value={country}>{country}</option>
            ))
          ) : (
            <option disabled>No countries available</option>
          )}
        </select>
      </div>
      <div>
        <Plot data={bar1Chart?.data} layout={bar1Chart?.layout} />
        <Plot data={bar2Chart?.data} layout={bar2Chart?.layout} />
        <Plot data={lineChart?.data} layout={lineChart?.layout} />
      </div>
    </div>
  );
};

export default ComparisonPage;