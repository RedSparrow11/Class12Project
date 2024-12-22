from flask import Flask, render_template, redirect, url_for, flash, request
from flask_mysqldb import MySQL
import mysql.connector as conn 
from test_predict_race_order import get_predictions

app = Flask(__name__, template_folder='app/templates')
# Setup MySQL connection (make sure to configure your database details)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Welcome@01'
app.config['MYSQL_DB'] = 'f1_tracker_db'
mysql = MySQL(app)

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    
    # Query to get unique race names
    cursor.execute("SELECT DISTINCT name FROM races ORDER BY name;")
    race_names = cursor.fetchall()

    # Query to get years from 2016 to 2024
    cursor.execute("SELECT DISTINCT year FROM races WHERE year BETWEEN 2016 AND 2024 ORDER BY year;")
    years = cursor.fetchall()

    return render_template('home.html', race_names=race_names, years=years)


@app.route('/results', methods=['GET'])
def results_page():
    race_name = request.args.get('raceName')
    year = request.args.get('year')
    
    if not race_name or not year:
        return render_template(
            'results.html',
            race_name=race_name,
            year=year,
            results=None,
            predictions=None,
            error="Please select a valid race and year."
        )
    
    cursor = mysql.connection.cursor()
    
    # Query to fetch race results
    query = """
        SELECT 
            d.driverId,
            CONCAT(d.forename, ' ', d.surname) AS full_name,
            COALESCE(r.position, 'DNF') AS positionDisplay
        FROM results r
        LEFT JOIN drivers d ON r.driverId = d.driverId
        LEFT JOIN races ra ON r.raceId = ra.raceId
        WHERE ra.name = %s AND ra.year = %s
        ORDER BY r.positionOrder;
    """
    
    cursor.execute(query, (race_name, year))
    results = cursor.fetchall()
    
    if not results:
        # If no official results, fetch predictions
        predicted_results = get_predictions(race_name, int(year))  # Convert year to int
        
        # Convert list of tuples to a DataFrame
        import pandas as pd
        predicted_results_df = pd.DataFrame(predicted_results, columns=['Driver', 'Predicted Position'])
        
        # Convert DataFrame to HTML
        predictions_html = predicted_results_df.to_html(index=False, classes='table table-bordered')

        return render_template(
            'results.html',
            race_name=race_name,
            year=year,
            results=None,
            predictions=predictions_html,
            error="The race data for this event is unavailable. Below is a predicted order based on historical data."
        )
    
    # Pass the official results to the template
    return render_template('results.html', race_name=race_name, year=year, results=results, predictions=None)

@app.route('/driver/<int:driver_id>')
def driver_details(driver_id):
    # Query to fetch driver details along with their season results for each year
    driver_query = """
        SELECT
            d.driverId,
            d.driverRef,
            d.forename,
            d.surname,
            SUM(ds.points) AS total_points,
            SUM(ds.wins) AS total_wins,
            r.year AS season,
            MAX(ds.position) AS final_position
        FROM
            drivers d
        LEFT JOIN
            driver_standings ds ON d.driverId = ds.driverId
        LEFT JOIN
            races r ON r.raceId = ds.raceId
        WHERE
            d.driverId = %s
            AND r.year BETWEEN 2016 AND 2024
        GROUP BY
            d.driverId, r.year
        ORDER BY
            r.year;
    """

    cursor = mysql.connection.cursor()
    cursor.execute(driver_query, (driver_id,))
    driver_data = cursor.fetchall()

    # If no data is found, return an error message
    if not driver_data:
        flash("Driver data not found", "error")
        return redirect(url_for('home'))

    # Calculate the total points and total wins
    total_points = sum([data[4] for data in driver_data])  # data[4] is total_points
    total_wins = sum([data[5] for data in driver_data])    # data[5] is total_wins

    # Pass the results to the template
    return render_template(
        'driver_details.html',
        driver=driver_data[0],  # First entry to get driver info (can be used for basic driver info)
        total_points=total_points,
        total_wins=total_wins,
        seasons=driver_data  # All seasons data (results for each year)
    )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5500)
