import matplotlib.pyplot as plt
import numpy as np
import serial
import time

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

bufferLen = int(1e5)
optoData = np.zeros([2, bufferLen])
dataIndex = 0
serRead = ""
adcBits = 10

# Plot the first frame
line, = ax.plot(optoData[1, :], optoData[0, :], "bo")

# Opening a serial connection
ser = serial.Serial("COM3", 115200)
time.sleep(1)

updateRateNs = 1e9
elapsedTimeNs = 0
startTimeNs = time.time_ns()
lastUpdateNs = time.time_ns() - startTimeNs

# Initiating the data stream
startByte = bytearray()
startByte.append(0x01)
ser.write(startByte)

while True:
    if ser.in_waiting > 0:
        serRead = ser.readline().decode("utf-8").strip()
        elapsedTimeNs = time.time_ns() - startTimeNs
        optoData[0, dataIndex] = int(serRead)
        optoData[1, dataIndex] = elapsedTimeNs
        dataIndex = (dataIndex + 1) % bufferLen
        if elapsedTimeNs - lastUpdateNs >= updateRateNs:
            # Update the plot
            line.set_xdata(optoData[1, :])
            line.set_ydata(optoData[0, :])
            fig.canvas.draw()
            fig.canvas.flush_events()
            print("Figure redrawn")
            lastUpdateNs = time.time_ns() - startTimeNs

ser.close()

with open("datasets\\lastLiveStreamFrame.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(optoData)
