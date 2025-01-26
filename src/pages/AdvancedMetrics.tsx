import React, {useState, useEffect} from 'react';
import axios from "axios";

const AdvancedMetricsPage = () => {

    useEffect(() => {
        axios.get("http://127.0.0.1:5000")
        },[]);
    return ( 
        <div>
            <h1>Advanced Metrics Page</h1>
        </div>
     );        
    
};

export default AdvancedMetricsPage