import os
import time
import requests
import psycopg2
from psycopg2 import OperationalError, sql


def get_bounds():
    return {
        'lamin': float(os.getenv("LAMIN")),
        'lamax': float(os.getenv("LAMAX")),
        'lomin': float(os.getenv("LOMIN")),
        'lomax': float(os.getenv("LOMAX"))
    }



def connect_db(retries=5, delay=3):
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                dbname=os.getenv("DB_NAME", "flights"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASS", "postgres")
            )
            print("Connected to DB")
            return conn
        except OperationalError as e:
            print(f"DB connection failed (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("Could not connect to the database after retries")

def check_table_exists(conn, table_name="flight_snapshot"):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name=%s
            )
        """, (table_name,))
        exists = cur.fetchone()[0]
        if exists:
            print(f"Table '{table_name}' exists.")
        else:
            print(f"Table '{table_name}' does NOT exist.")
        return exists

def fetch_and_store(conn):
    
    # bounds = get_bounds()
    
    lamin,lomin,lamax,lomax = (45.8389, 5.9962,46.8371, 10.5526)
    
    bounds = {
        'lamin': lamin,
        'lamax': lamax,
        'lomin': lomin,
        'lomax': lomax
    }
    
    
    
    region = os.getenv("REGION", "global")
    
    r = requests.get("https://opensky-network.org/api/states/all", params=bounds)
    data = r.json()
    states = data.get("states", [])

    with conn.cursor() as cur:
        for s in states:
            if any(s[i] is None for i in [0, 1, 2, 3, 5, 6, 7, 9, 10, 13, 8]):
                print(f"Skipping incomplete record: {s}")
                print("None values found in the following fields: ", end="")
                print(", ".join(f"field {i}" for i in [0, 1, 2, 3, 5, 6, 7, 9, 10, 13, 8] if s[i] is None))
                continue
            
            print(f"Inserting record: {s[0]}, {s[1]}, {s[2]}, {s[3]}, {s[5]}, {s[6]}, {s[7]}, {s[9]}, {s[10]}, {s[13]}, {s[8]}")

            cur.execute("""
    INSERT INTO flight_snapshot (
        icao24, callsign, origin_country, time_position,
        latitude, longitude, altitude, velocity, true_track, vertical_rate,
        geo_altitude, on_ground, region
    ) VALUES (%s, %s, %s, to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    s[0], s[1], s[2], s[3], s[6], s[5], s[7], s[9], s[10], s[11], s[13], s[8], region
))

    conn.commit()
    print(f"{region} inserted {len(states)} flight records")

if __name__ == "__main__":
    conn = connect_db()

    if not check_table_exists(conn):
        print("You should create the 'flight_snapshot' table before running this script.")
        exit(1)

    fetch_and_store(conn)
    conn.close()
