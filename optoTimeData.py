import csv
import matplotlib.pyplot as plt
import numpy as np
import serial
import time

ser = serial.Serial("COM3", 115200)
time.sleep(1)

optoData = [[], [], []]
dataIndex = 0
serRead = ""
adcBits = 10

maxDataLogTimeNs = 2e9
startTimeNs = time.time_ns()
elapsedTimeNs = 0

startByte = bytearray()
startByte.append(0x01)
ser.write(startByte)

while elapsedTimeNs < maxDataLogTimeNs:
    if ser.in_waiting > 0:
        serRead = ser.readline().decode("utf-8").strip()
        optoData[dataIndex].append(int(serRead))
        # If writing the opto output (index 1) then also update/write the elapsed time
        if dataIndex == 1:
            elapsedTimeNs = time.time_ns() - startTimeNs
            optoData[2].append(elapsedTimeNs)
        dataIndex = (dataIndex + 1) % 2

ser.close()

with open("datasets\\optoTimeData.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(optoData)

optoData = np.array(optoData)

fig = plt.figure()
ax = fig.subplots(2)
ax[0].set_title("Optocoupler Inputs and Outputs vs Time")
ax[0].set_xlabel("Time (ns)")
ax[0].set_ylabel("Optocoupler input")
ax[0].plot(optoData[2], optoData[0], "b-")

ax[1].set_xlabel("Time (ns)")
ax[1].set_ylabel("Optocoupler output")
ax[1].plot(optoData[2], optoData[1], "b-")
fig.savefig("figures\\optoTimeData.png")
fig.show()
