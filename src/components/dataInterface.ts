export interface Order {
    orderId: string;
    customerId: string;
    productId: string; 
    orderDate: string, 
}

export interface Sale {
    orderId: string; 
    sales: number;
    profit: number;
    shippingCost: number; 
    shipMode: string; 
}

export interface Customer {
    customerId: string; 
    customerName: string; 
    country: string;
    city: string; 
}

export interface Product {
    productId: string; 
    productName: string;
    category: string;
    subCategory: string;
}

export interface DashboardFilters {
    dateRange: [Date | null, Date | null];  
    country: string | null;
    category: string | null;
    customerType: string | null;
}