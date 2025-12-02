# 📊 Target Brazil E-Commerce Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-0.9.0%2B-yellow?style=for-the-badge&logo=duckdb&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🚀 Project Overview

**Target Brazil E-Commerce Analytics** is a high-performance, interactive dashboard designed to analyze over 100,000 orders from Target's operations in Brazil (2016-2018). Built with **Streamlit** and powered by **DuckDB**, this application transforms raw CSV data into actionable business insights through a premium, dark-mode user interface.

The dashboard provides a 360-degree view of the e-commerce ecosystem, covering sales trends, customer demographics, logistics performance, payment behaviors, and product reviews.

---

## 🎨 Key Features & UI Sections

The application is structured into **8 intuitive tabs**, each designed for specific analytical needs:

### 1. 🏠 Overview
- **Executive Summary**: High-level KPIs including Total Revenue, Total Orders, Unique Customers, and Average Order Value.
- **Trend Visualization**: Interactive time-series charts showing order volume and revenue growth over time.
- **Quick Insights**: At-a-glance metrics for immediate business assessment.

### 2. 📈 Orders & Trends
- **Temporal Analysis**: Deep dive into seasonality, monthly trends, and year-over-year growth.
- **Time-of-Day Analysis**: Breakdown of ordering patterns by time of day (Dawn, Morning, Afternoon, Night).
- **Interactive Charts**: Dynamic Plotly area and bar charts for granular trend exploration.

### 3. 🌍 Geography
- **Geospatial Intelligence**: Interactive maps and charts visualizing customer distribution across Brazil's 26 states.
- **Regional Performance**: State-wise breakdown of orders, revenue, and freight costs.
- **City-Level Data**: Top cities by order volume and revenue.

### 4. 💰 Economy
- **Financial Health**: Analysis of average ticket size and freight costs relative to order value.
- **Cost Evolution**: Tracking the percentage increase in order costs and freight over the years.
- **State Economics**: Comparative analysis of economic indicators across different regions.

### 5. 🚚 Delivery & Freight
- **Logistics Performance**: Analysis of delivery times, including estimated vs. actual delivery duration.
- **Freight Optimization**: Identification of states with the highest and lowest freight costs.
- **Efficiency Metrics**: Top performing regions for delivery speed and reliability.

### 6. 💳 Payments
- **Payment Preferences**: Distribution of payment methods (Credit Card, Boleto, Voucher, Debit Card).
- **Installment Analysis**: Insights into customer installment choices and their impact on order value.
- **Trend Correlation**: Relationship between payment types and seasonal sales spikes.

### 7. ⭐ Products & Reviews
- **Product Performance**: Top-selling product categories and revenue drivers.
- **Customer Sentiment**: Analysis of review scores and their distribution.
- **Quality Metrics**: Correlation between delivery time and customer satisfaction ratings.

### 8. 📋 Raw Tables
- **Data Explorer**: Full access to the underlying raw datasets (Customers, Orders, Products, etc.).
- **"ALL TABLES" View**: Seamlessly scroll through previews of all 8 datasets in a single view.
- **Export Capability**: Download any table or query result directly as a CSV file.
- **System Logs**: Built-in activity log to track user interactions and system performance.

---

## 🛠️ Tech Stack

This project leverages a modern, robust technology stack to ensure performance, scalability, and a premium user experience:

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) - For building the interactive web application.
- **Database Engine**: [DuckDB](https://duckdb.org/) - An in-process SQL OLAP database for lightning-fast query execution on CSV files.
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/) - For advanced data transformation and handling.
- **Visualization**: [Plotly](https://plotly.com/python/) - For creating interactive, publication-quality graphs and charts.
- **Styling**: Custom **CSS** & **HTML** - Injected for a bespoke, dark-mode aesthetic with glassmorphism effects.

---

## 📂 File Structure

```
Target SQL/
├── streamlit_app.py          # Main application entry point
├── run_target_queries.py     # SQL query definitions and DuckDB execution logic
├── Walmart_app.py            # Reference design file
├── data/                     # Directory containing the 8 source CSV files
│   ├── customers.csv
│   ├── orders.csv
│   ├── products.csv
│   └── ...
├── .agent/                   # Agent configuration and workflows
└── README.md                 # Project documentation
```

---

## 📜 License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2025 Ratnesh Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact

**RATNESH SINGH**

- 📧 Email: [rattudacsit2021gate@gmail.com](mailto:rattudacsit2021gate@gmail.com)
- 💼 LinkedIn: [https://www.linkedin.com/in/ratneshkumar1998/](https://www.linkedin.com/in/ratneshkumar1998/)
- 🐙 GitHub: [https://github.com/Ratnesh-181998](https://github.com/Ratnesh-181998)
- 📱 Phone: +91-947XXXXX46

### Project Links
- 🌐 Live Demo: [Streamlit App](https://walmart-black-friday-sales-analysis-3hrmdpouwmapvucuwcg8r7.streamlit.app/)
- 📖 Documentation: [GitHub Wiki](https://github.com/Ratnesh-181998/Target-Brazil-E-Commerce-Analytics/wiki)
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/Ratnesh-181998/Target-Brazil-E-Commerce-Analytics/issues)
