import React, {useEffect, useState} from 'react';
import Plot from "react-plotly.js";
import axios from "axios";
import "../designs/CountriesPage.css"; 

type PlotlyChartData = {
    data: any[];
    layout: Record<string, any>;
  };
const CountriesPage = () => {
    const [countries, setCountries] = useState<string[]>([]);
    const [selectedCountry, setSeleectedCountry] = useState("");
    // Sales in period graph
    const [sales_over_time, set_Sales_over_time] = useState<PlotlyChartData | null>(null);
    // Profit in period grpah 
    const [profit_over_time, set_Profit_over_time] = useState<PlotlyChartData | null>(null);
    // Top 10 costumers graph
    const [top_costumers, set_Top_costuomers] = useState<PlotlyChartData | null>(null);
    // Shipping Mode graph 
    const [shipping_mode, set_Shipping_mode] = useState<PlotlyChartData | null>(null);
    // Sunburst graph
    const [sunburst_products, setSunburst_products] = useState<PlotlyChartData | null>(null);
    const [profit, setProfit] = useState("");
    const [len_customers, setLen_customers] = useState("");
    const [len_orders, setLen_orders] = useState("");
    const [len_products, setLen_products] = useState("");
    const [total_sales, setTotal_sales] = useState("");
    const [shipping_cost, setShipping_cost] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [years, setYears] = useState<string[]>([]);
    const [selectedYear, setSelectedYear] = useState("all");
    const [cities, setCities] = useState<string[]>([]);
    const [selectedCities, setSelectedCities] = useState("all");

    useEffect(() => {
        axios.get("https://flask-serverless.onrender.com/countries")
            .then((response) => {
                setCountries(response.data.countries);
                if (response.data.countries.length > 0) {
                    setSeleectedCountry(response.data.countries[0]);
                }
            })
            .catch((error) => console.error("Error fetching countries data", error));
    }, []);

    useEffect(() => {
        if (selectedCountry) {
            axios.get(`https://flask-serverless.onrender.com/countries/${selectedCountry}/cities`)
                .then((response) => {
                    setCities(response.data.cities);
                    setSelectedCities("all");
                })
                .catch((error) => console.error("Error fetching years data", error));
        }
    }, [selectedCountry]);
    

    useEffect(() => {
        if (selectedCountry) {
            axios.get(`https://flask-serverless.onrender.com/countries/${selectedCountry}/years`)
                .then((response) => {
                    setYears(response.data.years);
                    setSelectedYear("all");
                })
                .catch((error) => console.error("Error fetching years data", error));
        }
    }, [selectedCountry]);

    useEffect(() => {
        if (selectedCountry) {
            setIsLoading(true);
            axios.get(`https://flask-serverless.onrender.com/countries/${selectedCountry}/${selectedYear}/${selectedCities}`)
                .then((response) => {
                    setProfit(response.data.total_profit);
                    setLen_customers(response.data.customers);
                    setLen_orders(response.data.orders);
                    setLen_products(response.data.products);
                    setTotal_sales(response.data.total_sales);
                    setShipping_cost(response.data.shipping_costs);
                    set_Sales_over_time(response.data.sales_over_time);
                    set_Top_costuomers(response.data.top_costumers);
                    set_Shipping_mode(response.data.shipping_mode);
                    set_Profit_over_time(response.data.profit_over_time);
                    setSunburst_products(response.data.sunburst_products);
                    setIsLoading(false);
                })
                .catch((error) => {
                    console.error("Error fetching country data", error);
                    setIsLoading(false);
                });
        }
    }, [selectedCountry, selectedYear, selectedCities]);

    const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSeleectedCountry(e.target.value);
    } 

    const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedYear(e.target.value);
    };

    const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedCities(e.target.value);
    };

    return ( 
        <div>
            <h1>Country Statistics </h1>
            <div>
                <label htmlFor="countryDropDown">Select a Country: </label>
                <select onChange={handleCountryChange} id="countryDropdown" value={selectedCountry}>
                    {countries.length > 0 ? (
                        countries.map((country) => (
                            <option key={country} value={country}>{country}</option>
                        ))
                    ) : (
                        <option disabled>No countries available</option>
                    )}
                </select>
            </div>
            <br />
            <div>
                <label htmlFor="cityDropdown">Select a City: </label>
                <select onChange={handleCityChange} id="cityDropdown" value={selectedCities}>
                    <option value="all">All Cities</option>
                    {cities && cities.map((city) => (
                        <option key={city} value={city}>{city}</option>
                    ))}
                </select>
            </div>
            <br />
            <div>
                <label htmlFor="yearDropdown">Select a Year: </label>
                <select onChange={handleYearChange} id="yearDropdown" value={selectedYear}>
                    <option value="all">All Years</option>
                    {years && years.map((year) => (
                        <option key={year} value={year}>{year}</option>
                    ))}
                </select>
            </div>
            <div className="metrics-container">
                <div className="metric-card">
                    <div className="metric-title">Total Profit</div>
                    <div className="metric-value">{profit}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Customers</div>
                    <div className="metric-value">{len_customers}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Orders</div>
                    <div className="metric-value">{len_orders}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Products</div>
                    <div className="metric-value">{len_products}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Shipping Cost</div>
                    <div className="metric-value">{shipping_cost}</div>
                </div>
                <div className="metric-card">
                    <div className="metric-title">Total Sales</div>
                    <div className="metric-value">{total_sales}</div>
                </div>
            </div>
            <br /><br />
            {isLoading ? (
                <p>Loading...</p>
            ) : (
                <>  
                    <Plot data={sunburst_products?.data} layout={sunburst_products?.layout} />
                    <Plot data={sales_over_time?.data} layout={sales_over_time?.layout} />
                    <Plot data={profit_over_time?.data} layout={profit_over_time?.layout} config={{ responsive: true }}/>
                    <Plot data={top_costumers?.data} layout={top_costumers?.layout} />
                    <Plot data={shipping_mode?.data} layout={shipping_mode?.layout}/>
                </>
            )}
        </div>
    )
}

export default CountriesPage;