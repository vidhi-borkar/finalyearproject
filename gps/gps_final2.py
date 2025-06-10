import serial
import pynmea2

ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)

while True:
    newdata = ser.readline()
    print(newdata)

    if b'$GPRMC' in newdata:
        try:
            newmsg = pynmea2.parse(newdata.decode('utf-8'))
            lat = newmsg.latitude
            lng = newmsg.longitude
            gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
            print(gps)
        except pynmea2.ParseError as e:
            print("Parse error:", e)

