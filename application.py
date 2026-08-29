import joblib
import numpy as np
from config.paths_config import MODEL_DIR
from flask import Flask, render_template, request

app = Flask(__name__)

loaded_model = joblib.load(MODEL_DIR)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Converted floating points properly (since Yeo-Johnson transforms yield floats)
        lead_time = float(request.form["lead_time"])
        no_of_special_requests = float(request.form["no_of_special_requests"])
        avg_price_per_room = float(request.form["avg_price_per_room"])
        
        arrival_date = int(request.form["arrival_date"])
        arrival_month = int(request.form["arrival_month"])
        
        market_segment_type = float(request.form["market_segment_type"])
        total_stay_nights = int(request.form["total_stay_nights"])
        arrival_year = float(request.form["arrival_year"])
        
        total_guests = int(request.form["total_guests"])
        type_of_meal_plan = float(request.form["type_of_meal_plan"])
        
        features = np.array([[
            lead_time, no_of_special_requests, avg_price_per_room, 
            arrival_date, arrival_month, market_segment_type, 
            total_stay_nights, arrival_year, total_guests, type_of_meal_plan
        ]])
        
        prediction = loaded_model.predict(features)
        
        return render_template("index.html", prediction=int(prediction[0]))
    
    return render_template("index.html", prediction=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)