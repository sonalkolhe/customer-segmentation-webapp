import os
from typing import List, Dict, Union, Any

import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for, Response
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.io as pio
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.secret_key = 'super_secret_marketing_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate marketing insights and segmentation profiles based on clustered data.

    Args:
        df (pd.DataFrame): The DataFrame containing customer data and assigned clusters.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing details
        and marketing strategies for a specific cluster.
    """
    insights: List[Dict[str, Any]] = []

    cluster_means = df.groupby('Cluster')[
        ['Age', 'Annual Income (k$)', 'Spending Score (1-100)']
    ].mean()

    for cluster_id, row in cluster_means.iterrows():
        cluster_data = df[df['Cluster'] == cluster_id]

        avg_age = row['Age']
        income = row['Annual Income (k$)']
        score = row['Spending Score (1-100)']
        size = len(cluster_data)

        gender_counts = cluster_data['Gender'].value_counts(normalize=True)
        female_pct = round(gender_counts.get('Female', 0) * 100)
        male_pct = round(gender_counts.get('Male', 0) * 100)

        if female_pct > 55:
            gender_profile = "Female Dominated"
            gender_icon = "bi-gender-female"
        elif male_pct > 55:
            gender_profile = "Male Dominated"
            gender_icon = "bi-gender-male"
        else:
            gender_profile = "Balanced"
            gender_icon = "bi-gender-ambiguous"

        if income > 70 and score > 70:
            label = "VIP / Big Spenders"
            color = "success"
            if avg_age < 35:
                desc = (
                    "Young, wealthy, and loves to spend. Target for luxury "
                    "fashion and trending tech."
                )
                action = (
                    "Campaign: Instagram/TikTok Influencers promoting "
                    "exclusive 'Drops'."
                )
            else:
                desc = "Established wealth with high consumption habits."
                action = (
                    "Campaign: Exclusive VIP Club membership & Concierge services."
                )

        elif income > 70 and score < 40:
            label = "Wealthy Savers"
            color = "warning"
            desc = "High earning potential but careful with money."
            action = (
                "Campaign: Focus on 'Value for Money', Investment products, "
                "or 'Buy It For Life' quality."
            )

        elif income < 40 and score > 60:
            label = "Young Trendsetters"
            color = "info"
            desc = (
                "Likely students or young professionals spending on trends."
            )
            action = (
                "Campaign: Flash Sales, 'Buy Now Pay Later' offers, and "
                "discount coupons."
            )

        elif income < 40 and score < 40:
            label = "Budget Conscious"
            color = "secondary"
            desc = "Strict budget constraints. Only buys essentials."
            action = (
                "Campaign: Clearance sales, bulk discounts, and loyalty points."
            )

        else:
            label = "Average Customer"
            color = "primary"
            desc = "Steady income and average spending habits."
            action = (
                "Campaign: Standard newsletter, seasonal promotions, and "
                "retention offers."
            )

        insights.append({
            'cluster': cluster_id,
            'label': label,
            'color': color,
            'size': size,
            'avg_income': round(income, 1),
            'avg_score': round(score, 1),
            'avg_age': round(avg_age, 0),
            'gender_profile': gender_profile,
            'gender_icon': gender_icon,
            'female_pct': female_pct,
            'male_pct': male_pct,
            'desc': desc,
            'action': action
        })

    return insights


@app.route('/')
def index() -> str:
    """
    Render the index page.

    Returns:
        str: The rendered HTML for the index page.
    """
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze() -> Union[str, Response]:
    """
    Process the uploaded CSV file, perform KMeans clustering, and render results.

    Returns:
        Union[str, Response]: Rendered HTML template with analysis results or
        a redirect to the index page on error.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file: FileStorage = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            df = pd.read_csv(file)
            df.columns = [c.strip() for c in df.columns]

            required_cols = [
                'Gender', 'Age', 'Annual Income (k$)', 'Spending Score (1-100)'
            ]
            if not all(col in df.columns for col in required_cols):
                flash(
                    f'Error: CSV missing columns. Required: {", ".join(required_cols)}'
                )
                return redirect(url_for('index'))

            X = df[['Annual Income (k$)', 'Spending Score (1-100)']]
            kmeans = KMeans(
                n_clusters=5, init='k-means++', random_state=42, n_init=10
            )
            df['Cluster'] = kmeans.fit_predict(X)

            fig = px.scatter(
                df,
                x='Annual Income (k$)',
                y='Spending Score (1-100)',
                color=df['Cluster'].astype(str),
                title='Customer Segments',
                template='plotly_white',
                height=500,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )

            chart_html = pio.to_html(
                fig, full_html=False, include_plotlyjs='cdn'
            )

            insights = generate_insights(df)
            kpis = {
                'total_customers': len(df),
                'avg_income': round(df['Annual Income (k$)'].mean(), 2),
                'avg_score': round(df['Spending Score (1-100)'].mean(), 2)
            }

            return render_template(
                'results.html',
                chart_html=chart_html,
                insights=insights,
                kpis=kpis
            )

        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))

    flash('Invalid file type. Please upload a CSV.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)