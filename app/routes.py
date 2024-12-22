from flask import render_template, request
from . import app  # Import your app object to register routes with it
import mysql.connector

# Home page route
@app.route('/')
def index():
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your actual username
        password='Welcome@01',  # Replace with your actual password
        database='f1_tracker_db'  # Replace with your database name
    )
    cursor = connection.cursor(dictionary=True)

    # Query to fetch distinct race names
    cursor.execute("SELECT DISTINCT race_name FROM predictions")
    races = cursor.fetchall()

    # Close database connection
    cursor.close()
    connection.close()

    # Pass races to the homepage template
    return render_template('home.html', races=races)

# Results page route
@app.route('/results', methods=['POST'])
def results():
    # Fetch race name and year from the form
    race_name = request.form['race_name']
    year = request.form['year']

    # Connect to MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your actual username
        password='Welcome@01',  # Replace with your actual password
        database='f1_tracker_db'  # Replace with your database name
    )
    cursor = connection.cursor(dictionary=True)

    # Query to fetch predictions and dynamically calculate position
    query = """
    SELECT driver_id, 
        (SELECT name FROM drivers WHERE drivers.id = predictions.driver_id) AS driver_name,
        lap_time, pit_stop_lap, compound,
        RANK() OVER (ORDER BY lap_time ASC) AS position
    FROM predictions
    WHERE race_name = %s AND year = %s
    """
    cursor.execute(query, (race_name, year))
    predictions = cursor.fetchall()

    # Close database connection
    cursor.close()
    connection.close()

    # Pass predictions to the results template
    return render_template('results.html', predictions=predictions, race_name=race_name, year=year)

# Driver details page route
@app.route('/driver/<int:driver_id>')
def driver_details(driver_id):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your actual username
        password='Welcome@01',  # Replace with your actual password
        database='f1_tracker_db'  # Replace with your database name
    )
    cursor = connection.cursor(dictionary=True)

    # Query to fetch driver details, dynamically calculate total wins based on lap_time
    query = """
    SELECT d.name AS driver_name, d.team,
        COUNT(CASE WHEN p.lap_time = (SELECT MIN(lap_time) FROM predictions WHERE race_name = p.race_name AND year = p.year) THEN 1 END) AS wins,
        COUNT(p.id) AS races_participated,
        MIN(p.lap_time) AS best_lap_time, MAX(p.pit_stop_lap) AS max_pit_stop_lap
    FROM drivers d
    LEFT JOIN predictions p ON d.id = p.driver_id
    WHERE d.id = %s
    GROUP BY d.id
    """
    cursor.execute(query, (driver_id,))
    driver = cursor.fetchone()

    # Close database connection
    cursor.close()
    connection.close()

    # Pass driver details to the driver details template
    return render_template('driver_details.html', driver=driver)
