"""
model.py

Contains clustering models and functions 
to perform customer segmentation
based on Income vs Spending and Age vs Spending.
"""

import os
import pandas as pd
import joblib
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler

sns.set_style('whitegrid')

# Load pre-trained models
MODEL_FOLDER = os.path.join(os.getcwd(), 'model')
kmeans_income = joblib.load(os.path.join(MODEL_FOLDER, 'kmeans_income_spending.pkl'))
kmeans_age = joblib.load(os.path.join(MODEL_FOLDER, 'kmeans_age_spending.pkl'))

# Scalers for standardization
scaler_income = StandardScaler()
scaler_age = StandardScaler()


def df_to_base64_plot(df, x_col, y_col, cluster_col, title, palette='viridis'):
    """
    Generate a scatter plot and return it as a base64 string
    """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x=x_col,
        y=y_col,
        hue=cluster_col,
        palette=palette,
        s=100,
        alpha=0.8,
        edgecolor='black'
    )
    plt.title(title)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64


def cluster_income(file_path):
    """
    Perform clustering on 'Annual Income' vs 'Spending Score' and return:
    - CSV path
    - Plot as base64
    - Cluster summary as dict
    """
    df = pd.read_csv(file_path)
    df_features = df[['Annual Income (k$)', 'Spending Score (1-100)']]
    X_scaled = scaler_income.fit_transform(df_features)

    df['Income_Cluster'] = kmeans_income.predict(X_scaled)

    # Save CSV
    out_file = os.path.join('downloads', f'clustered_income_{os.path.basename(file_path)}')
    df.to_csv(out_file, index=False)

    # Generate plot
    img_base64 = df_to_base64_plot(
        df, 
        x_col='Annual Income (k$)', 
        y_col='Spending Score (1-100)',
        cluster_col='Income_Cluster',
        title='Income vs Spending Segments',
        palette='viridis'
    )

    # Generate cluster insights
    cluster_summary = df.groupby('Income_Cluster')[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].mean().round(2)
    cluster_summary['Size'] = df['Income_Cluster'].value_counts()
    insights = cluster_summary.to_dict(orient='index')

    return {
        "csv_url": out_file,
        "plot_base64": img_base64,
        "insights": insights
    }


def cluster_age(file_path):
    """
    Perform clustering on 'Age' vs 'Spending Score' and return:
    - CSV path
    - Plot as base64
    - Cluster summary as dict
    """
    df = pd.read_csv(file_path)
    df_features = df[['Age', 'Spending Score (1-100)']]
    X_scaled = scaler_age.fit_transform(df_features)

    df['Age_Cluster'] = kmeans_age.predict(X_scaled)

    # Save CSV
    out_file = os.path.join('downloads', f'clustered_age_{os.path.basename(file_path)}')
    df.to_csv(out_file, index=False)

    # Generate plot
    img_base64 = df_to_base64_plot(
        df, 
        x_col='Age', 
        y_col='Spending Score (1-100)', 
        cluster_col='Age_Cluster', 
        title='Age vs Spending Segments',
        palette='magma'
    )

    # Generate cluster insights
    cluster_summary = df.groupby('Age_Cluster')[['Age','Annual Income (k$)','Spending Score (1-100)']].mean().round(2)
    cluster_summary['Size'] = df['Age_Cluster'].value_counts()
    insights = cluster_summary.to_dict(orient='index')

    return {
        "csv_url": out_file,
        "plot_base64": img_base64,
        "insights": insights
    }
