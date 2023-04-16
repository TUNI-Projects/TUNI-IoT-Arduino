import serial

ser = serial.Serial('/dev/ttyACM0', 38400)

while True:
    data = ser.readline().decode().strip().split(',')
    data = list(map(float, data[:6])) + [int(data[6])]
    print("Sensor data: ", data)