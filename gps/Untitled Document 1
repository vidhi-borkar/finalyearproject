import gps
import time

# Connect to the gpsd daemon
session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

print("Waiting for GPS fix...")

try:
    while True:
        report = session.next()

        # Only process TPV (Time-Position-Velocity) reports
        if report['class'] == 'TPV':
            lat = getattr(report, 'lat', None)
            lon = getattr(report, 'lon', None)
            alt = getattr(report, 'alt', None)
            speed = getattr(report, 'speed', None)

            if lat is not None and lon is not None:
                print(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}", end='')
                if alt is not None:
                    print(f", Altitude: {alt:.2f} m", end='')
                if speed is not None:
                    print(f", Speed: {speed:.2f} m/s", end='')
                print()
            else:
                print("Waiting for GPS fix...")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")

