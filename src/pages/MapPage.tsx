import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";

type PlotlyChartData = {
    data: any[];
    layout: Record<string, any>;
  };

const MapPage = () => {
    const [profitData, setProfitChartData] = useState<PlotlyChartData | null>(null);
    const [shippingData, setShippingChartData] = useState<PlotlyChartData | null>(null);
    const [costumerData, setCostumerChartData] = useState<PlotlyChartData | null>(null);

  useEffect(() => {
    axios.get("https://flask-serverless.onrender.com/map")
      .then((response) => {
        setProfitChartData(response.data.map_profit_fig);
        setShippingChartData(response.data.map_shipping_fig);
        setCostumerChartData(response.data.map_customers_fig);
    })
      .catch((error) => console.error("Error fetching map data:", error));
  }, []);

  return (
    <div>
      <h1>World Map Analysis</h1>
      <Plot data={profitData?.data} layout={profitData?.layout} />
      <Plot data={shippingData?.data} layout={shippingData?.layout} />
      <Plot data={costumerData?.data} layout={costumerData?.layout}/>
    </div>
  );
};

export default MapPage;