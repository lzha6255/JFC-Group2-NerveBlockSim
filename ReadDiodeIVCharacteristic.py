import csv
import matplotlib.pyplot as plt
import numpy as np
import serial
import time

ser = serial.Serial("COM3", 115200)
time.sleep(1)

adcBits = 10
adcData = [[], [], []]
serRead = ""
dataSetIndex = 0

startByte = bytearray()
startByte.append(0x01)
# Start the process
ser.write(startByte)

while True:
    if ser.in_waiting:
        serRead = ser.readline().decode("utf-8").strip()
        if serRead == "END":
            break
        adcData[dataSetIndex].append(int(serRead))
        print(dataSetIndex)
        dataSetIndex = (dataSetIndex + 1) % 3
print(adcData)

# Write the dataset to a file
with open("datasets\\adcReading.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(adcData)

# Convert the dataset to a numpy array
adcData = np.array(adcData)
print(adcData)

# Plot the raw data from the ADC
rawDataFig = plt.figure()
rawDataAx = rawDataFig.subplots()
rawDataAx.set_title("Raw ADC Reading")
rawDataAx.set_xlabel("Input Voltage Reading (A0)")
rawDataAx.set_ylabel("Output Voltage Reading (A1)")
rawDataAx.plot(adcData[1], adcData[2], "bo")
rawDataFig.savefig("figures\\adcReading.png")
rawDataFig.show()

# Excluding PWM duty cycle data and dividing by ADC range to get real voltage
diodeVoltageData = adcData[1:3, :] * 5 / (2 ** adcBits)
print(diodeVoltageData)

# Finding the first derivative. This will give us the value of R_diode
derivative = []
for i in range(1, diodeVoltageData.shape[1] - 1):
    derivative.append((diodeVoltageData[1, i+1] - diodeVoltageData[1, i-1]) / (diodeVoltageData[0, i+1] - diodeVoltageData[0, i-1]))
dVoutdVin = np.append([diodeVoltageData[0, 1:diodeVoltageData.shape[1]-1]], np.array([derivative]), 0)

# Finding the second derivative. This will give us the value of V_diode
secondDerivative = []
for i in range(1, dVoutdVin.shape[1] - 1):
    secondDerivative.append((dVoutdVin[1, i+1] - dVoutdVin[1, i-1]) / (dVoutdVin[0, i+1] - dVoutdVin[0, i-1]))
d2VoutdVin2 = np.append([dVoutdVin[0, 1:dVoutdVin.shape[1]-1]], np.array([secondDerivative]), 0)
print(dVoutdVin)

# Plot the diode voltages and analysis
fig = plt.figure()
fig.tight_layout(h_pad=0.5)
ax = fig.subplots(3)
fig.suptitle("Diode voltages and derivatives")
ax[0].set_title("Voltage")
ax[0].set_xlabel(r"$V_{in}$ (V)")
ax[0].set_ylabel(r"$V_{out}$ (V)")
ax[0].plot(diodeVoltageData[0], diodeVoltageData[1], "bo")

ax[1].set_title("First Derivative")
ax[1].set_xlabel(r"$V_{in}$ (V)")
ax[1].set_ylabel(r"$\frac{dV_{out}}{dV_{in}}$")
ax[1].plot(dVoutdVin[0], dVoutdVin[1], "bo")

ax[2].set_title("Second Derivative")
ax[2].set_xlabel(r"$V_{in}$ (V)")
ax[2].set_ylabel(r"$\frac{d^2V_{out}}{dV_{in}^2}$")
ax[2].plot(d2VoutdVin2[0], d2VoutdVin2[1], "bo")

fig.savefig("figures\\diodeVoltages.png")
fig.show()

ser.close()
