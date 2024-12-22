from flask import Flask, render_template, request
import mysql.connector
import pandas as pd

app = Flask(__name__)

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Welcome@01',
    'database': 'f1_tracker_db'
}

allowed_drivers = [
    'Max Verstappen', 'Sergio Perez', 'Lewis Hamilton', 'George Russell', 'Lando Norris',
    'Oscar Piastri', 'Charles Leclerc', 'Carlos Sainz', 'Esteban Ocon', 'Pierre Gasly',
    'Alex Albon', 'Franco Colapinto', 'Zhou Guanyu', 'Valtteri Bottas', 'Yuki Tsunoda',
    'Liam Lawson', 'Kevin Magnussen', 'Nico Hulkenberg', 'Fernando Alonso', 'Lance Stroll'
]

def get_predictions(circuit_name, year):
    year = int(year)  # Convert year to int
    connection = mysql.connector.connect(**db_config)

    # SQL queries
    results_query = f"""
        SELECT raceId, driverId, positionOrder 
        FROM results 
        WHERE raceId IN (
            SELECT raceId 
            FROM races 
            WHERE circuitId = (
                SELECT circuitId 
                FROM circuits 
                WHERE name = '{circuit_name}'
            ) AND year BETWEEN 2016 AND {year - 1}
        );
    """

    driver_standings_query = f"""
        SELECT raceId, driverId, points 
        FROM driver_standings 
        WHERE raceId IN (
            SELECT raceId 
            FROM races 
            WHERE circuitId = (
                SELECT circuitId 
                FROM circuits 
                WHERE name = '{circuit_name}'
            ) AND year BETWEEN 2016 AND {year - 1}
        );
    """

    drivers_query = """
        SELECT driverId, CONCAT(forename, ' ', surname) AS driver_name
        FROM drivers;
    """

    # Fetch data
    results_data = pd.read_sql(results_query, connection)
    driver_standings_data = pd.read_sql(driver_standings_query, connection)
    driver_data = pd.read_sql(drivers_query, connection)

    # Filter driver data to include only allowed drivers
    driver_data = driver_data[driver_data['driver_name'].isin(allowed_drivers)]

    # Combine data
    combined_data = pd.merge(
        results_data[['raceId', 'driverId', 'positionOrder']],
        driver_standings_data[['raceId', 'driverId', 'points']],
        on=['raceId', 'driverId'],
        how='left'
    )
    combined_data = combined_data.fillna(0)

    combined_data = pd.merge(combined_data, driver_data, on='driverId', how='inner')

    # Calculate ranks
    combined_data['position_rank'] = combined_data.groupby('driverId')['positionOrder'].transform('mean')
    combined_data['points_rank'] = combined_data.groupby('driverId')['points'].transform('mean')
    combined_data['final_rank'] = combined_data[['position_rank', 'points_rank']].mean(axis=1)

    predicted_order = combined_data.groupby(['driverId', 'driver_name'], as_index=False)['final_rank'].mean()
    predicted_order = predicted_order.rename(columns={'final_rank': 'predicted_position'})
    predicted_order = predicted_order.sort_values(by='predicted_position')

    # Ensure all drivers are included
    all_drivers_df = pd.DataFrame({'driver_name': allowed_drivers})
    predicted_order = pd.merge(all_drivers_df, predicted_order, on='driver_name', how='left')
    max_rank = predicted_order['predicted_position'].max()
    predicted_order['predicted_position'] = predicted_order['predicted_position'].fillna(max_rank + 1)
    predicted_order['predicted_position'] = range(1, len(predicted_order) + 1)

    # Rename columns for user-friendly table headings
    predicted_order = predicted_order.rename(columns={
    'driver_name': 'Driver',
    'predicted_position': 'Predicted Position'
})


    connection.close()

    return predicted_order