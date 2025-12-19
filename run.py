# from flask import Flask, request, jsonify
# import os
# import matplotlib.pyplot as plt
# import io
# import base64
# from app.model import cluster_income, cluster_age  

# app = Flask(__name__)

# # Ensure upload folder exists
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# # Health check
# @app.route('/api/v1/health', methods=['GET'])
# def health():
#     return jsonify({"status": "UP", "message": "API is running"})


# # Income segmentation
# @app.route('/api/v1/segment/income', methods=['POST'])
# def income_segmentation():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(file_path)
#     out_file = cluster_income(file_path)
#     return jsonify({"csv_url": out_file})


# # Age segmentation
# @app.route('/api/v1/segment/age', methods=['POST'])
# def age_segmentation():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(file_path)
#     out_file = cluster_age(file_path)
#     return jsonify({"csv_url": out_file})


# # Chart endpoint
# @app.route('/chart')
# def chart():
#     plt.figure(figsize=(4, 3))
#     plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
#     plt.title("Sample Chart")
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     buf.seek(0)
#     plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#     return jsonify({"plot_base64": plot_base64})


# if __name__ == "__main__":
#     app.run(debug=True)
# from flask import Flask, render_template, request, jsonify
# import os
# from app.model import cluster_income, cluster_age

# app = Flask(__name__)

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/analyze", methods=["POST"])
# def analyze():
#     file = request.files.get("file")
#     if not file:
#         return "No file uploaded", 400

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(file_path)

#     income_result = cluster_income(file_path)
#     age_result = cluster_age(file_path)

#     return render_template(
#         "result.html",
#         income_data=income_result,
#         age_data=age_result
#     )

# # API health check (optional but good)
# @app.route("/api/v1/health")
# def health():
#     return jsonify({"status": "UP"})

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0")
from flask import Flask, request, jsonify
import os
import matplotlib.pyplot as plt
import io
import base64
from app.model import cluster_income, cluster_age  
import traceback

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "UP", "message": "API is running"})

@app.route('/api/v1/segment/income', methods=['POST'])
def income_segmentation():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        out_file = cluster_income(file_path)
        return jsonify({"csv_url": out_file})

    except Exception as e:
        app.logger.error(f"Income segmentation error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/segment/age', methods=['POST'])
def age_segmentation():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        out_file = cluster_age(file_path)
        return jsonify({"csv_url": out_file})

    except Exception as e:
        app.logger.error(f"Age segmentation error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/chart')
def chart():
    try:
        plt.figure(figsize=(4, 3))
        plt.plot([1, 2, 3, 4], [10, 20, 25, 30])
        plt.title("Sample Chart")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        return jsonify({"plot_base64": plot_base64})
    except Exception as e:
        app.logger.error(f"Chart generation error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
