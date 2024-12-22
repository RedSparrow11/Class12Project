CREATE TABLE IF NOT EXISTS status (
    statusId VARCHAR(255) PRIMARY KEY,
    status VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS circuits (
    circuitId INT PRIMARY KEY,
    circuitRef VARCHAR(255),
    name VARCHAR(255),
    location VARCHAR(255),
    country VARCHAR(255),
    lat FLOAT,
    lng FLOAT,
    alt INT,
    url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS seasons (
    year INT PRIMARY KEY,
    url VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS drivers (
    driverId INT PRIMARY KEY,
    driverRef VARCHAR(255),
    number INT,
    code VARCHAR(255),
    forename VARCHAR(255),
    surname VARCHAR(255),
    dob DATE,
    nationality VARCHAR(255),
    url VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS constructors (
    constructorId INT PRIMARY KEY,
    constructorRef VARCHAR(255),
    name VARCHAR(255),
    nationality VARCHAR(255),
    url VARCHAR(255)
);




CREATE TABLE IF NOT EXISTS races (
    raceId INT PRIMARY KEY,
    year INT,
    round INT,
    circuitId INT,
    name VARCHAR(255),
    date DATE,
    time TIME,
    url VARCHAR(255),
    fp1_date DATE,
    fp1_time TIME,
    fp2_date DATE,
    fp2_time TIME,
    fp3_date DATE,
    fp3_time TIME,
    quali_date DATE,
    quali_time TIME,
    sprint_date DATE,
    sprint_time TIME,
    FOREIGN KEY (circuitId) REFERENCES circuits(circuitId)
);



CREATE TABLE IF NOT EXISTS results (
    resultId INT PRIMARY KEY,
    raceId INT,
    driverId INT,
    constructorId INT,
    number INT,
    grid INT,
    position INT,
    positionText VARCHAR(255),
    positionOrder INT,
    points INT,
    laps INT,
    time VARCHAR(255),
    milliseconds INT,
    fastestLap INT,
    _rank_ INT,
    fastestLapTime VARCHAR(255),
    fastestLapSpeed FLOAT,
    statusId VARCHAR(255),
    FOREIGN KEY (raceId) REFERENCES races(raceId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId),
    FOREIGN KEY (statusId) REFERENCES status(statusId)
);

CREATE TABLE IF NOT EXISTS sprint_results (
    resultId INT PRIMARY KEY,
    raceId INT,
    driverId INT,
    constructorId INT,
    number INT,
    grid INT,
    position INT DEFAULT NULL,
    positionText VARCHAR(255),
    positionOrder INT,
    points INT,
    laps INT,
    time VARCHAR(255),
    milliseconds INT,
    fastestLap INT,
    fastestLapTime VARCHAR(255),
    statusId VARCHAR(255)

);




CREATE TABLE IF NOT EXISTS qualifying (
    qualifyId INT PRIMARY KEY,
    raceId INT,
    driverId INT,
    constructorId INT,
    number INT,
    position INT,
    q1 TIME,
    q2 TIME,
    q3 TIME,
    FOREIGN KEY (driverId) REFERENCES drivers(driverId),
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId)
);

CREATE TABLE IF NOT EXISTS pit_stops (
    raceId INT,
    driverId INT,
    stop INT,
    lap INT,
    time TIME,
    duration TIME,
    milliseconds INT,
    FOREIGN KEY (driverId) REFERENCES drivers(driverId)
);

CREATE TABLE IF NOT EXISTS lap_times (
    raceId INT,
    driverId INT,
    lap INT,
    position INT,
    time TIME,
    milliseconds INT,
    PRIMARY KEY (raceId, driverId, lap),
    FOREIGN KEY (raceId) REFERENCES races(raceId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId)
);


CREATE TABLE IF NOT EXISTS driver_standings (
    driverStandingsId INT PRIMARY KEY,
    raceId INT,
    driverId INT,
    points INT,
    position INT,
    positionText VARCHAR(255),
    wins INT,
    FOREIGN KEY (raceId) REFERENCES races(raceId),
    FOREIGN KEY (driverId) REFERENCES drivers(driverId)
);


CREATE TABLE IF NOT EXISTS constructor_standings (
    constructorStandingsId INT PRIMARY KEY,
    raceId INT,
    constructorId INT,
    points INT,
    position INT,
    positionText VARCHAR(255),
    wins INT,
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId)
);

CREATE TABLE IF NOT EXISTS constructor_results (
    constructorResultsId INT PRIMARY KEY,
    raceId INT,
    constructorId INT,
    points INT,
    status VARCHAR(255),
    FOREIGN KEY (constructorId) REFERENCES constructors(constructorId)
);




ALTER TABLE drivers
ADD COLUMN average_position FLOAT;


ALTER TABLE drivers
ADD COLUMN podiums INT;


-- To get the average position for each driver
SELECT driverId, AVG(positionOrder) AS average_position
FROM results
WHERE positionOrder IS NOT NULL
GROUP BY driverId;

-- To get the podium count (drivers who finished in top 3 positions)
SELECT driverId, COUNT(*) AS podiums
FROM results
WHERE positionOrder <= 3
GROUP BY driverId;




UPDATE drivers d
SET d.average_position = (
    SELECT AVG(r.positionOrder)
    FROM results r
    WHERE r.driverId = d.driverId
)
WHERE EXISTS (
    SELECT 1
    FROM results r
    WHERE r.driverId = d.driverId
);


UPDATE drivers d
SET d.podiums = (
    SELECT COUNT(*)
    FROM results r
    WHERE r.driverId = d.driverId AND r.positionOrder <= 3
)
WHERE EXISTS (
    SELECT 1
    FROM results r
    WHERE r.driverId = d.driverId
);
