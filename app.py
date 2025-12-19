import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for
from sklearn.cluster import KMeans
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'super_secret_marketing_key'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_insights(df):
    insights = []
    
    # Group by Cluster to calculate means
    # numeric_only=True ensures we don't try to average the "Gender" text column
    cluster_means = df.groupby('Cluster')[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].mean()
    
    for cluster_id, row in cluster_means.iterrows():
        # Get raw data for this specific cluster to count gender
        cluster_data = df[df['Cluster'] == cluster_id]
        
        avg_age = row['Age']
        income = row['Annual Income (k$)']
        score = row['Spending Score (1-100)']
        size = len(cluster_data)
        
        # Calculate Gender Dominance
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

        # --- SEGMENTATION LOGIC ---
        
        # 1. High Spenders
        if income > 70 and score > 70:
            label = "VIP / Big Spenders"
            color = "success" # Green
            if avg_age < 35:
                desc = "Young, wealthy, and loves to spend. Target for luxury fashion and trending tech."
                action = "Campaign: Instagram/TikTok Influencers promoting exclusive 'Drops'."
            else:
                desc = "Established wealth with high consumption habits."
                action = "Campaign: Exclusive VIP Club membership & Concierge services."

        # 2. High Income, Low Spend
        elif income > 70 and score < 40:
            label = "Wealthy Savers"
            color = "warning" # Yellow
            desc = "High earning potential but careful with money."
            action = "Campaign: Focus on 'Value for Money', Investment products, or 'Buy It For Life' quality."

        # 3. Low Income, High Spend
        elif income < 40 and score > 60:
            label = "Young Trendsetters"
            color = "info" # Blue
            desc = "Likely students or young professionals spending on trends."
            action = "Campaign: Flash Sales, 'Buy Now Pay Later' offers, and discount coupons."

        # 4. Low Income, Low Spend
        elif income < 40 and score < 40:
            label = "Budget Conscious"
            color = "secondary" # Grey
            desc = "Strict budget constraints. Only buys essentials."
            action = "Campaign: Clearance sales, bulk discounts, and loyalty points."

        # 5. Average
        else:
            label = "Average Customer"
            color = "primary" # Blue
            desc = "Steady income and average spending habits."
            action = "Campaign: Standard newsletter, seasonal promotions, and retention offers."

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
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        try:
            # Read CSV
            df = pd.read_csv(file)
            
            # Clean column names
            df.columns = [c.strip() for c in df.columns]

            # Validation
            required_cols = ['Gender', 'Age', 'Annual Income (k$)', 'Spending Score (1-100)']
            if not all(col in df.columns for col in required_cols):
                flash(f'Error: CSV missing columns. Required: {", ".join(required_cols)}')
                return redirect(url_for('index'))

            # KMeans Clustering
            X = df[['Annual Income (k$)', 'Spending Score (1-100)']]
            kmeans = KMeans(n_clusters=5, init='k-means++', random_state=42, n_init=10)
            df['Cluster'] = kmeans.fit_predict(X)

            # Visualization
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
            
            chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

            # Insights & KPIs
            insights = generate_insights(df)
            kpis = {
                'total_customers': len(df),
                'avg_income': round(df['Annual Income (k$)'].mean(), 2),
                'avg_score': round(df['Spending Score (1-100)'].mean(), 2)
            }

            return render_template('results.html', chart_html=chart_html, insights=insights, kpis=kpis)

        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
            
    flash('Invalid file type. Please upload a CSV.')
    return redirect(url_for('index'))

# THIS IS THE CRITICAL PART THAT WAS MISSING
if __name__ == '__main__':
    app.run(debug=True)