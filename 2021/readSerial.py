import serial, time
print('running...')
#Serial takes two parameters: serial device and baudrate
ser = serial.Serial('/dev/ttyS0', 14400)
ser.reset_input_buffer()
data=b''
while 1:
    char = ser.read(1)
    if char[0] > 31 and char[0] < 127:
        data += char
    if char[0] == 13:
        print(data.decode("utf-8"))
        data=b''
ser.close()