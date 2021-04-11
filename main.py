import googlemaps
from flask import Flask
from flask import request
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
map_client = googlemaps.Client(API_KEY)

app = Flask(__name__)

def distance(begin,end,mode):
    #distance_float in km, implied_time_float in terms of % of hour, implied_speed_float in terms of km per hour
    export = map_client.distance_matrix(begin,end,mode)
    distance_extract = export['rows'][0]['elements'][0]['distance']['value']
    duration_extract = export['rows'][0]['elements'][0]['duration']['value']
    distance_float = float(distance_extract/1000) #convert to km
    implied_time_float = float(duration_extract/3600) #convert to hour
    implied_speed_float = distance_float / implied_time_float
    return distance_float,implied_time_float, implied_speed_float

def calories_formula(KPH,WKG,T,mode):
    #assumes 0% grade: http://www.shapesense.com/fitness-exercise/calculators/walking-calorie-burn-calculator.shtml
    if mode=='walking':
        calories = (0.0215*KPH**3 - 0.1765*KPH**2 + 0.8710*KPH + 1.4577)*WKG*T
        return calories
    #assumes MET average of 8: https://onlinecalculator.info/calories-burned-biking-calculator-p22
    if mode=='bicycling':
        calories = (T * 60 * 8 * 3.5 * WKG) / 200
        return calories
    else:
        return "An error occurred, my bad!"

@app.route('/')
def index():
    begin_address = request.args.get("begin_address", "")
    end_address = request.args.get("end_address", "")
    weight = request.args.get("weight", "")
    mode = request.args.get("mode", "")
    if begin_address and end_address and weight and mode:
        total_calories = calories_counter(begin_address,end_address,weight,mode)
        return (
            """<title>Calories Estimator</title>  <div class="header">
            <h1>Calories Estimator For Travel</h1></div>
            <form action="" method="get">
                Beginning address: <input type="text" name="begin_address" style="width: 300px"><br>
                Ending address: <input type="text" name="end_address" style="width: 300px"><br>
                Current weight (in pounds): <input type="text" name="weight" style="width: 35px"><br>
                Current mode of transport: <input type="radio" id="walking" name="mode" value="walking">
                <label for="walking">walking</label>
                <input type="radio" id="bicycling" name="mode" value="bicycling">
                <label for="bicycling">bicycling</label><br><br>
                <input type="submit" value="Calculate Calories Burned"><br>
            </form>"""
        + "Approx. Calories Burned: "
        + total_calories
        + """<br><iframe width="600" height="450" style="border:0" loading="lazy" allowfullscreen
            src="https://www.google.com/maps/embed/v1/directions?key={}
            &origin={}
            &destination={}
            &mode={}"></iframe>
    """).format(API_KEY,begin_address,end_address,mode)
    else:
        total_calories = ""
        return (
            """<title>Calories Estimator</title>  <div class="header">
            <h1>Calories Estimator For Travel</h1></div>
            <form action="" method="get">
                Beginning address: <input type="text" name="begin_address" style="width: 300px"><br>
                Ending address: <input type="text" name="end_address" style="width: 300px"><br>
                Current weight (in pounds): <input type="text" name="weight" style="width: 35px"><br>
                Current mode of transport: <input type="radio" id="walking" name="mode" value="walking">
                <label for="walking">walking</label>
                <input type="radio" id="bicycling" name="mode" value="bicycling">
                <label for="bicycling">bicycling</label><br><br>
                <input type="submit" value="Calculate Calories Burned"><br>
            </form>""")

def calories_counter(begin,end,weight,mode):
    #assumes speed and time based on google maps API
    try:
        distance_float = distance(begin,end,mode)[0]
        time_float = distance(begin,end,mode)[1]
        speed_float = distance(begin,end,mode)[2]
        calories_burned = calories_formula(speed_float,float(weight)*0.453592,time_float,mode)
        return str(round(calories_burned))
    except:
        return "An error occurred, sorry :("

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8080, debug=True)

