from flask import Flask, render_template, send_file, request
import psycopg2
import io
import pandas as pd
import pickle

app = Flask(__name__)

# Database connection settings
DATABASE = {
    'dbname': 'IDBMS DATASETS',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',  # or your database host
    'port': '5432'        # default PostgreSQL port
}

# Function to connect to the PostgreSQL database
def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE)
        return conn
    except Exception as e:
        print("Database Not Connected:", e)
        return None

# Load the normalizer and model
with open('normalizer.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('xgb_model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dataset')
def dataset():
    return render_template('dataset.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/image_error')
def image_error():
    return render_template('image_error.html')

@app.route('/get_image/<image_id>')
def get_image(image_id):
    conn = get_db_connection()
    
    if not conn:
        return render_template('image_error.html')

    cursor = conn.cursor()

    # Fetch the image from the database
    cursor.execute("SELECT plot FROM plots WHERE id = %s", (image_id,))
    image_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if image_data:
        image = io.BytesIO(image_data[0])
        return send_file(image, mimetype='image/png')
    else:
        return "Image not found", 404

@app.route('/predict', methods=['POST'])
def predict_rul():
    try:
        # Extract sensor data from the form
        engine = int(request.form.get('engine'))
        time = float(request.form.get('time'))
        setting1 = float(request.form.get('setting1'))
        setting2 = float(request.form.get('setting2'))
        setting3 = float(request.form.get('setting3'))
        
        # Collect only necessary sensor values
        sensor_values = {
            's2': float(request.form.get('sensor2')),
            's3': float(request.form.get('sensor3')),
            's4': float(request.form.get('sensor4')),
            's7': float(request.form.get('sensor7')),
            's8': float(request.form.get('sensor8')),
            's9': float(request.form.get('sensor9')),
            's11': float(request.form.get('sensor11')),
            's12': float(request.form.get('sensor12')),
            's13': float(request.form.get('sensor13')),
            's14': float(request.form.get('sensor14')),
            's15': float(request.form.get('sensor15')),
            's17': int(request.form.get('sensor17')),
            's20': float(request.form.get('sensor20')),
            's21': float(request.form.get('sensor21')),
        }

        # Combine inputs into a single DataFrame row
        input_data = pd.DataFrame([sensor_values])

        # Normalize the input data
        input_data_scaled = scaler.transform(input_data)

        # Predict the RUL using the model
        predicted_rul = model.predict(input_data_scaled)[0]

        # Render the result.html template with the prediction result
        return render_template('result1.html', predicted_rul=predicted_rul)

    except Exception as e:
        return f"An error occurred: {str(e)}", 500  # Return server error

if __name__ == '__main__':
    app.run(debug=False)
