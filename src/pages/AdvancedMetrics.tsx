import React, {useState, useEffect} from 'react';
import axios from "axios";
import Plot from "react-plotly.js";

type PlotlyChartData = {
    data: any[];
    layout: Record<string, any>;
  };

const AdvancedMetricsPage = () => {
    const [kMeansChart, setkMeansChart] = useState<PlotlyChartData | null>(null);
    const [seasonalChart, setSeasonalChart] = useState<PlotlyChartData | null>(null);
    const [trendingChart, setTrendingChart] = useState<PlotlyChartData | null>(null);
    const [countryTrendingChart, setCountryTrendingChart] = useState<PlotlyChartData | null>(null);
    const [highValue, setHighValue] = useState<PlotlyChartData | null>(null);

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/advanced_metrics").then((response) => {
            setkMeansChart(response.data.kmeans);
            setSeasonalChart(response.data.seasonal);
            setTrendingChart(response.data.trending);
            setCountryTrendingChart(response.data.sales_growth);
            setHighValue(response.data.high_value);
        })
        },[]);
    return ( 
        <div>
            <h1>Advanced Metrics Page</h1>
            <div>
                <Plot data={kMeansChart?.data} layout={kMeansChart?.layout} />
                <Plot data={seasonalChart?.data} layout={seasonalChart?.layout} />
                <Plot data={trendingChart?.data} layout={trendingChart?.layout} />
                <Plot data={countryTrendingChart?.data} layout={countryTrendingChart?.layout} />
                <Plot data={highValue?.data} layout={highValue?.layout} />
            </div>
        </div>
     );        
    
};

export default AdvancedMetricsPage