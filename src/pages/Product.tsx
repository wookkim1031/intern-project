import React, {useEffect, useState} from 'react';
import axios from "axios";
import Plot from "react-plotly.js";

type PlotlyChartData = {
    data: any[];
    layout: Record<string, any>;
  };

const Product = () => {
    const [product, setProduct] = useState("all");
    const [products, setProducts] = useState<string[]>([]);
    const [country, setCountry] = useState("all");
    const [countries, setCountries] = useState<string[]>([]);
    const [city, setCity] = useState("all");
    const [cities, setCities] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [salesOverTime, setSalesOverTime] = useState<PlotlyChartData | null>(null);
    const [profitOverTime, setProfitOverTime] = useState<PlotlyChartData | null>(null);

    useEffect(() => {
        axios.get(`https://flask-serverless.onrender.com/products`)
            .then((response) => {
                setProducts(response.data.products);
                setCountries(response.data.countries);
                setCities(response.data.cities);
            })
            .catch((error) => console.error("Error fetching products data", error));
    },[]);

    // after product changes 
    // countries and cities need to be changed
    // TODO: when couuntries and cities change the product also has to change
    useEffect(() => {
        if(product !== "all") {
            axios.get(`https://flask-serverless.onrender.com/products/${product}/${country}/${city}`)
            .then((response) => {
                setCountries(response.data.countries_list || []);
                setCities(response.data.cities_list || []);
            })
            .catch((error) => {
                console.error("Error fetching countries data", error);
            });
        } else {
            axios.get(`https://flask-serverless.onrender.com/products`)
            .then((response) => {
                setCountries(response.data.countries);
                setCities(response.data.cities);
            }).catch((error) => {
                console.error("Error fetching countries data", error);
            });
        }},[product]);

    // change when the product and country variable changes 
    useEffect(() => {
        if(product !== "all" && country !== "all") {
            axios.get(`https://flask-serverless.onrender.com/products/${product}/${country}/${city}`)
                .then((response) => {
                    setCities(response.data.cities_lists || []);
                    setCity("all");
                })
                .catch((error) => {
                    console.error("Error fetching cities data", error);
                })
        }
    }, [product, country]);

    useEffect(() => {
        setLoading(true);
        axios.get(`https://flask-serverless.onrender.com/products/${product}/${country}/${city}`)
            .then((response) => {
                setSalesOverTime(response.data.sales_over_time);
                setProfitOverTime(response.data.profit_over_time);
                setLoading(false);
            })
            .catch((error) => {
                console.log("Error fetching data", error);
                setLoading(false);
            })
    },[product, country, city]);

    const handleProductChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setProduct(e.target.value);
    }

    const handleCountryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setCountry(e.target.value);
    }

    const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setCity(e.target.value);
    };

    return (
        <div>
            <h1>Product Analysis</h1>
                        <div>
                <label>Product: </label>
                <select onChange={handleProductChange} name="productDropdown" value={product}>
                    <option value="all">All Products</option>
                    {products.length > 0 ? (
                        products.map((product) => (
                            <option key={product} value={product}>
                                {product}
                            </option>
                        ))
                    ) : (
                        <option disabled>No products available</option>
                    )}
                </select>
            </div>
            <div>
                <label>Country: </label>
                <select onChange={handleCountryChange} name="countryDropdown" value={country}>
                    <option value="all">All Countries</option>
                    {countries.length > 0 ? (
                        countries.map((country) => (
                            <option key={country} value={country}>
                                {country}
                            </option>
                        ))
                    ) : (
                        <option disabled>No countries available</option>
                    )}
                </select>
            </div>
            <div>
                <label>City: </label>
                <select onChange={handleCityChange} name="cityDropdown" value={city}>
                    <option value="all">All Cities</option>
                    {cities.length > 0 ? (
                        cities.map((city) => (
                            <option key={city} value={city}>
                                {city}
                            </option>
                        ))
                    ) : (
                        <option disabled>No cities available</option>
                    )}
                </select>
            </div>
            {loading ? (
            <p>Loading...</p>
            ) : (
            <>
                <Plot data={salesOverTime?.data} layout={salesOverTime?.layout} />
                <Plot data={profitOverTime?.data} layout={profitOverTime?.layout} />
            </>
            )}
        </div>
        );
    };
        
    export default Product;