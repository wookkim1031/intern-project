import React, {useState, useEffect} from 'react';
import type {Order, Sale, Product, Customer,DashboardFilters} from "./dataInterface"
import Papa from 'papaparse';
import axios from "axios";

interface ParsedData {
  [keyof: string]: string;
}

export default function Dashboard() {
    const [filters, setFilters] = useState<DashboardFilters>({
        dateRange: [null, null],
        country: null,
        category: null,
        customerType: null,
    });
    const [query, setQuery] = useState(''); 
    const [sales, setSales] = useState<ParsedData[]>([]);
    const [orders, setOrders] = useState<ParsedData[]>([]);
    const [products, setProducts] = useState<ParsedData[]>([]);
    const [customers, setCustomers] = useState<ParsedData[]>([]);
    const [accuracy, setAccuracy] = useState<number | null>(null);
    const [showImport, setShowImport] = useState(true);
    const [csvData, setCsvData] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [csvUrl, setCsvUrl] = useState<string>("");

    const handleProcessCsv = async () => {
      
      try {
        const response = await axios.post("/api/process", { csv_url: csvUrl });
  
        setAccuracy(response.data.accuracy); 
        setError(null); 
      } catch (err: any) {
        setError(err.response?.data?.error || "An error occurred during processing.");
      }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type:string) => {
        const file = e.target.files?.[0];
        if (file) {
            Papa.parse(file, {
              header:true,
              skipEmptyLines: true,
              complete: (result) => {
                const data = result.data as ParsedData[];

                switch(type) {
                  case 'orders':
                    setOrders(data);
                    break;
                  case 'sales':
                    setSales(data);
                    break;
                  case 'products':
                    setProducts(data);
                    break;
                  case 'customers':
                    setCustomers(data);
                    break;
                  default:
                    setError("Invalid file type");
                }

                switch(type) {
                  case 'orders':
                }
              },
              error: (error) => {
                console.error("Error parsing CSV: ", error);
              }
            });
        }
    }

    return (
    <div>
      <h2>Upload CSV FIles: Orders.csv, Sales.csv, Customers.csv, and Products.csv</h2>
      <div>
        <button onClick={handleProcessCsv}>
            Process CSV
        </button>
        {accuracy !== null && <p>Model Accuracy: {accuracy.toFixed(2)}</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}
        <label>
          Orders Table: 
          <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, 'orders')}/>
        </label>
      </div>
      <div>
        <label>
          Sales Table: 
          <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, 'orders')}/>
        </label>
      </div>
      <div>
        <label>
          Customers Table: 
          <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, 'orders')}/>
        </label>
      </div>
      <div>
        <label>
          Products Table: 
          <input type="file" accept=".csv" onChange={(e) => handleFileChange(e, 'orders')}/>
        </label>
      </div>

      <hr />
      <h2>Uploaded Data:</h2>

      <h3>Orders Table</h3>
      <table>
        <thead>
          {orders.length > 0 && (
            <tr>
              {Object.keys(orders[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          )}
        </thead>
        <tbody>
          {orders.map((row, index) => (
            <tr key={index}>
              {Object.values(row).map((value, i) => (
                <td key={i}>{value}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}   