import React, {useState, useEffect} from 'react';
import type {Order, Sale, Product, Customer,DashboardFilters} from "./dataInterface"

export default function Dashboard() {
    const [filters, setFilters] = useState<DashboardFilters>({
        dateRange: [null, null],
        country: null,
        category: null,
        customerType: null,
    });
    const [query, setQuery] = useState(''); 
    const [sales, setSales] = useState<Sale[]>([]);
    const [orders, setOrders] = useState<Order[]>([]);
    const [products, setProducts] = useState<Product[]>([]);
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [showImport, setShowImport] = useState(true);

    return (
    <div>
      <h1>Dashboard</h1>
    </div>
  );
}   