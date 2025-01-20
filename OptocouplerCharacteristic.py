import csv
import matplotlib.pyplot as plt
import numpy as np
import serial
import time

ser = serial.Serial("COM3", 115200)
time.sleep(1)

optoData = [[], []]
dataIndex = 0
serRead = ""
adcBits = 10

startByte = bytearray()
startByte.append(0x01)
ser.write(startByte)

while True:
    if ser.in_waiting > 0:
        serRead = ser.readline().decode("utf-8").strip()
        if serRead == "END":
            break
        optoData[dataIndex].append(int(serRead))
        dataIndex = (dataIndex + 1) % 2

ser.close()

with open("datasets\\optoData.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(optoData)

optoData = np.array(optoData)
# optoData = optoData * 5 / (2 ** adcBits)

fig = plt.figure()
ax = fig.subplots()
ax.set_title("4N25 Optocoupler input-output characteristic")
ax.set_xlabel("Diode Forward Voltage (V)")
ax.set_ylabel("Emitter Voltage (V)")
ax.plot(optoData[0], optoData[1], "b-")
fig.savefig("figures\\optoData.png")
fig.show()
