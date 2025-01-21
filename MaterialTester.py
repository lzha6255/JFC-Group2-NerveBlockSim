import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import csv

class MaterialTester:
    def __init__(self, name, stimLowRange = 0.2, stimHighRange = 0.4, port = "COM3", baudrate = 115200, sampleTimeNs = 5e9):
        self.name = name
        self.stimRanges = [stimLowRange, stimHighRange]
        # datasets arranged as follows: [[low range timestamps], [low range samples], [high range timestamps], [high
        # range samples]]
        self.samples = [[], [], [], []]
        self.indexer = {True : 0, False : 2}
        # Collection of samples that are determined to be during stimuplex active state
        self.activeSamples = [[], []]
        self.sampleTimeNs = sampleTimeNs
        self.serialPort = port
        self.baudrate = baudrate

    """
    The sampleUc function sends a signal to the Arduino to begin streaming analogRead() values across serial.
    These values are received and appended to a corresponding array in samples along with the timestamp in nanoseconds.
    iOffset is the index of the array to be written to within the samples array. Set iOffset to 0 when sampling at the
    low range of stimuplex current and to 2 when sampling at the high range of stimuplex current.
    """
    def sampleUc(self, lowRange):
        i = self.indexer[lowRange]
        ser = serial.Serial(self.serialPort, self.baudrate)

        # Clearing any existing data for the relevant dataset
        self.samples[i] = []
        self.samples[i+1] = []

        # Time variables
        elapsedTimeNs = 0
        startTimeNs = time.time_ns()

        # Send signal to start streaming data across
        signal = bytearray()
        signal.append(0x01)
        ser.write(signal)

        # Sample the uc for the sample period
        while (elapsedTimeNs < self.sampleTimeNs):
            if (ser.in_waiting > 0):
                serRead = ser.readline().decode("utf-8").strip()
                elapsedTimeNs = time.time_ns() - startTimeNs
                self.samples[i].append(elapsedTimeNs)
                self.samples[i+1].append(int(serRead))

        # Send signal to stop streaming data across
        ser.write(signal)

        ser.close()

    """
    plotData plots one of the datasets using matplotlib and saves the figure.
    iOffset is the starting index of the dataset to be plotted. The figure is saved to fpath.
    """
    def plotData(self, lowRange, fpath, title, xAxisLabel, yAxisLabel):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_title(title)
        ax.set_xlabel(xAxisLabel)
        ax.set_ylabel(yAxisLabel)
        ax.plot(self.samples[self.indexer[lowRange]], self.samples[1 + self.indexer[lowRange]], "b-")

        fig.savefig(fpath)
        fig.show()

    def plotActiveSamples(self, lowRange, fpath, title, xAxisLabel, yAxisLabel):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.set_title(title)
        ax.set_xlabel(xAxisLabel)
        ax.set_ylabel(yAxisLabel)

        i = int(self.indexer[lowRange] / 2)
        xData = range(len(self.activeSamples[i]))
        ax.plot(xData, self.activeSamples[i], "b-")

        fig.savefig(fpath)
        fig.show()

    def saveData(self, fpath):
        with open(fpath, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.samples)

    """
    This function aims to isolate any data samples that are taken when the stimuplex is actively driving current
    through the sensing loop.
    """
    def isolateActivePulseSamples(self, lowRange):
        optoData = np.array(self.samples[self.indexer[lowRange]+1])
        avgSample = np.average(optoData)
        i = int(self.indexer[lowRange] / 2)
        for sample in optoData:
            if sample > avgSample:
                self.activeSamples[i].append(sample)
