import React, {useEffect, useState} from 'react';
import Plot from "react-plotly.js";
import axios from "axios";

const CountriesPage = () => {
    const [countries, setCountries] = useState([]);
    const [selectedCountry, setSeleectedCountry] = useState("");
    const [chartData, setChartData] = useState(null);

    useEffect(() => {
        axios.get("localhost:5000/countries").then((response) => {
            const countryNames = response.data.countries;
            setCountries(countryNames);
            if (countryNames.length > 0) {
                setSeleectedCountry(countryNames[0]);
            }
        }
    ).catch((error) => console.error("Error fetching countries data" ,error));
    }, []);

    useEffect(() => {
        if(selectedCountry) {
            axios.get(`localhost:5000/countries/${selectedCountry}`).then((response) => {
                setChartData(response.data);
            } ).catch((error) => console.error("Error fetching country data", error));
        }
    }, [selectedCountry]);

    const handleCountryChange = (e) => {
        setSeleectedCountry(e.target.value);
    } 

    if (!chartData) {
        return <div>Loading...</div>;
    }
    
    return ( 
        <div>
            <h1>Country Statistics </h1>
            <div>
                <label htmlFor="countryDropDown">Select a Country: </label>
                <select onChange={handleCountryChange} id="countryDropdown" value={selectedCountry}>
                    {countries.map((country) => (
                        <option key={country} value={country}>{country}</option>
                    ))}
                </select>
            </div>
            {chartData ? (
                <Plot data={chartData.data} layout={chartData.layout}/> 
            ) : (
                <div>Loading...</div>)}
        </div>
    )
}

export default CountriesPage;