import csv
import mysql.connector

# Define column mappings
column_mappings = {
    "status": ["statusId", "status"],
    "circuits": ["circuitId", "circuitRef","name", "location", "country", "lat", "lng", "alt", "url"],
    "seasons": ["year", "url"],
    "drivers": ["driverId", "driverRef", "number", "code", "forename", "surname", "dob", "nationality", "url"],
    "constructors": ["constructorId", "constructorRef", "name", "nationality", "url"],
    "races": ["raceId", "year", "round","circuitId", "name", "date", "time", "url", "fp1_date",	"fp1_time",	"fp2_date",	"fp2_time",	"fp3_date",	"fp3_time",	"quali_date", "quali_time", "sprint_date", "sprint_time"],
    'results': ['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid', 'position', 'positionText', 'positionOrder', 'points', 'laps', 'time', 'milliseconds', 'fastestLap',"_rank_", 'fastestLapTime',"fastestLapSpeed", 'statusId'],
    'sprint_results': ['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid', 'position', 'positionText', 'positionOrder', 'points', 'laps', 'time', 'milliseconds', 'fastestLap', 'fastestLapTime', 'statusId'],
    "qualifying": ["qualifyId", "raceId", "driverId", "constructorId","number", "position", "q1", "q2", "q3"],
    "pit_stops": ["raceId", "driverId", "stop", "lap", "time", "duration", "milliseconds"],
    "lap_times": ["raceId", "driverId", "lap", "position", "time", "milliseconds"],
    "driver_standings": ["driverStandingsId", "raceId", "driverId", "points", "position", "positionText", "wins"],
    "constructor_standings": ["constructorStandingsId", "raceId", "constructorId", "points", "position", "positionText", "wins"],
    "constructor_results": ["constructorResultsId", "raceId", "constructorId", "points", "status"],
    
}


# Define CSV file paths
csv_files = {
    "status": "/Users/vaibhav/Downloads/f1db_csv/status.csv",
    "sprint_results": "/Users/vaibhav/Downloads/f1db_csv/sprint_results.csv",
    "seasons": "/Users/vaibhav/Downloads/f1db_csv/seasons.csv",
    "results": "/Users/vaibhav/Downloads/f1db_csv/resultscopy.csv",
    "races": "/Users/vaibhav/Downloads/f1db_csv/races.csv",
    "qualifying": "/Users/vaibhav/Downloads/f1db_csv/qualifying.csv",
    "pit_stops": "/Users/vaibhav/Downloads/f1db_csv/pit_stops.csv",
    "lap_times": "/Users/vaibhav/Downloads/f1db_csv/lap_times.csv",
    "drivers": "/Users/vaibhav/Downloads/f1db_csv/drivers.csv",
    "driver_standings": "/Users/vaibhav/Downloads/f1db_csv/driver_standings.csv",
    "constructors": "/Users/vaibhav/Downloads/f1db_csv/constructors.csv",
    "constructor_standings": "/Users/vaibhav/Downloads/f1db_csv/constructor_standings.csv",
    "constructor_results": "/Users/vaibhav/Downloads/f1db_csv/constructor_results.csv",
    "circuits": "/Users/vaibhav/Downloads/f1db_csv/circuits.csv",
}

# Function to load data from CSV
def load_data_from_csv(connection, table_name, file_path, columns):
    cursor = connection.cursor()
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Replace '\N' with None to handle NULL values
            data = [row[column] if row[column] != "\\N" else None for column in columns]
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            cursor.execute(insert_query, data)
    connection.commit()

# Main function
def main():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Welcome@01",
        database="f1_tracker_db"
    )

    for table, columns in column_mappings.items():
        print(f"Creating table {table}...")
        try:
            file_path = csv_files[table]
            load_data_from_csv(connection, table, file_path, columns)
            print(f"Loaded data into {table}.")
        except Exception as e:
            print(f"Error loading data for table {table}: {e}")

    connection.close()

if __name__ == "__main__":
    main()
