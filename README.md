# Segmently: AI-Powered Customer Segmentation Tool

**Segmently** is a modern SaaS-style web application designed to help marketers and businesses unlock hidden patterns in their customer data. By leveraging Machine Learning (K-Means Clustering), Segmently transforms raw customer data into actionable segments with visual insights and strategic marketing recommendations.

---

## 🚀 Key Features

* **Smart Data Processing:** Upload your customer CSV file via a drag-and-drop interface with automatic validation.
* **AI Segmentation Engine:** Uses the K-Means algorithm to group customers based on **Annual Income** and **Spending Score**.
* **Interactive Visualization:** Features a dynamic Plotly scatter plot that allows users to explore clusters interactively.
* **Deep Customer Insights:**
    * **Demographic Profiling:** Analyzes Average Age and Gender distribution (Male/Female dominance) for each cluster.
    * **Financial Metrics:** Calculates Average Income and Spending Score per segment.
    * **Actionable Strategies:** automatically generates marketing recommendations (e.g., "Target with VIP offers" or "Use Discount Coupons") based on the cluster's profile.
* **Responsive Dashboard:** A professional, clean UI built with Bootstrap 5, featuring KPI cards and grid-based insight layouts.

---

## 📂 Project Structure

The project follows a standard Flask MVC (Model-View-Controller) structure for scalability and maintainability.

```text
customer_segmentation_app/
│
├── app.py                # Main Flask Application (Backend & ML Logic)
├── requirements.txt      # List of Python dependencies
├── static/
│   └── css/
│       └── style.css     # Custom Styling (cards, animations, layout)
├── templates/
│   ├── index.html        # Landing Page (Hero section & File Upload)
│   └── results.html      # Dashboard Page (Graphs, KPIs & Insights)
└── uploads/              # (Auto-created) Temporary folder for uploaded CSVs