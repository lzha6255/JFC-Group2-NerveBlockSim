import serial
import time
import matplotlib.pyplot as plt
import csv

class ResistanceTester:
    def __init__(self, port="COM3", baudrate=9600, sampleFreq=2):
        self.port = port
        self.baudrate = baudrate
        self.sampleFreq = sampleFreq
        # Array of [[timestamps, samples]]
        self.samples = [[], []]
        self.resistanceData = []
        self.ADCBits = 10

    def sample(self, stableCutOff=True, stabilityLimit=10, stabilityWindow = 1, timeLimit=60):
        # Clearing data
        self.samples = [[], []]

        ser = serial.Serial(self.port, self.baudrate)

        sampling = True
        startTime = time.time()

        # Start signal
        signal = bytearray()
        signal.append(0x01)
        ser.write(signal)

        while sampling:
            if ser.in_waiting > 0:
                serRead = ser.readline().decode("utf-8").strip()
                self.samples[0].append(time.time()-startTime)
                self.samples[1].append(int(serRead))
                print(serRead)

                if stableCutOff:
                    # Check if the last stabilityLimit seconds of data have been constant
                    sampleLimit = stabilityLimit * self.sampleFreq
                    if len(self.samples[0]) < sampleLimit:
                        continue
                    sampling = False
                    value = self.samples[1][-1]
                    for i in range(1, sampleLimit):
                        if self.samples[1][-i] > value + stabilityWindow or self.samples[1][-i] < value - stabilityWindow:
                            sampling = True
                            print("Failed stability test at " + str(i))
                            break
                else:
                    if self.samples[0][-1] > timeLimit:
                        sampling = False

        ser.write(signal)

        ser.close()

    """
    Calculates the test material's resistance for all samples.
    Results are stored in self.resistanceData.
    """
    def ADCRead2Resistance(self, r, vcc=5):
        r = float(r)
        vcc = float(vcc)
        # Clearing data
        self.resistanceData = []

        for sample in self.samples[1]:
            v = float(sample) * vcc / (2 ** self.ADCBits)
            rGel = r * (vcc / v - 1)
            self.resistanceData.append(rGel)

    def plotResistance(self, fname, title="Resistance over time", xlabel="Time (s)", ylabel=r"Resistance ($\Omega$)"):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.plot(self.samples[0], self.resistanceData, "b-")

        fig.savefig(fname + ".png")
        fig.show()

    def saveData(self, fname):
        with open("datasets\\" + fname + ".csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.samples)
            writer.writerow(self.resistanceData)
