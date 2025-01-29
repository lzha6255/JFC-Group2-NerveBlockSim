import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import csv
import heapq

class MaterialTester:
    def __init__(self, name, stimLowRange = 0.2, stimHighRange = 0.4, port = "COM3", baudrate = 115200, sampleTimeNs = 5e9, stimFreq = 2):
        self.name = name
        self.stimRanges = [stimLowRange, stimHighRange]
        # datasets arranged as follows: [[low range timestamps], [low range samples], [high range timestamps], [high
        # range samples]]
        self.samples = [[], [], [], []]
        self.indexer = {True : 0, False : 2}
        # Collection of samples that are determined to be during stimuplex active state
        self.activeSamples = [[], []]
        # vLin = averaged out pulse analogRead() values used to calculate a linear motor response
        self.vLin = np.zeros(2)
        # linResponseParams = [m, b] where motor signal M = mv + b, v is the analogRead() value.
        self.linResponseParams = np.zeros(2)
        # Indices of activeSamples which delineate groups of data points from the same pulse
        self.pulseIndices = [[], []]
        self.sampleTimeNs = sampleTimeNs
        self.serialPort = port
        self.baudrate = baudrate
        self.stimFreq = stimFreq
        # Dataset of corresponding currents (i), distances (d), and output voltages (v)
        self.idvData = [[], [], []]

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
        ax.plot(xData, self.activeSamples[i], "bo")
        # Add vertical lines to delineate separate pulses
        for pulseIndex in self.pulseIndices[i]:
            ax.axvline(pulseIndex - 0.5, color = "r")

        fig.savefig(fpath)
        fig.show()

    def saveData(self, fname):
        with open(fname + "_raw.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.samples)

        with open(fname + "_peaks.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.activeSamples)

        with open(fname + "_peaks_metadata.txt", "w") as file:
            for pulseIndices in self.pulseIndices:
                file.write(str(len(pulseIndices)) + " pulses identified.\n")
                lastPulseIndex = 0
                pulseNumber = 1
                for pulseIndex in pulseIndices:
                    file.write(str(pulseIndex - lastPulseIndex) + " datapoints attributed to pulse " + str(pulseNumber) + "\n")
                    lastPulseIndex = pulseIndex
                    pulseNumber = pulseNumber + 1

    """
    This function aims to isolate any data samples that are taken when the stimuplex is actively driving current
    through the sensing loop.
    It does this by extracting all samples that are above the average over the entire dataset.
    """
    def aboveAveragePulseSamples(self, lowRange):
        optoData = np.array(self.samples[self.indexer[lowRange]+1])
        avgSample = np.average(optoData)
        i = int(self.indexer[lowRange] / 2)
        self.activeSamples[i] = []
        for sample in optoData:
            if sample > avgSample:
                self.activeSamples[i].append(sample)

    """
    Another function to isolate data samples from when the stimuplex is active.
    This one takes a more sophisticated approach of successively extracting maximums over the entire dataset and
    grouping them by their timestamps, until sample time * stimuplex frequency groups have been identified.
    """
    def groupMaxSamples(self, lowRange):
        # The samples within a group are guaranteed to be within this time frame inclusive
        groupTimeFrameNs = 1e3

        # Tupulize the dataset into a list of (sample, timestamp) pairs
        optoData = []
        for i in range(0, len(self.samples[self.indexer[lowRange]])):
            optoData.append((self.samples[self.indexer[lowRange]+1][i] * -1, self.samples[self.indexer[lowRange]][i]))
        # Heapify
        heapq.heapify(optoData)

        totalGroups = int(self.stimFreq * self.sampleTimeNs / 1e9)

        groups = []

        while len(groups) < totalGroups:
            dataPoint = heapq.heappop(optoData)
            # Reverse the order of the tuple and multiply analog reading by -1
            dataPoint = (dataPoint[1], dataPoint[0] * -1)
            # Step through the groups and try to allocate the data point to one
            allocated = False
            for group in groups:
                if dataPoint[0] <= group[0][0] + groupTimeFrameNs and dataPoint[0] >= group[-1][0] - groupTimeFrameNs:
                    heapq.heappush(group, dataPoint)
                    allocated = True
                    break
            # Create a new group if not allocated
            if not allocated:
                group = [dataPoint]
                heapq.heapify(group)
                groups.append(group)

        i = int(self.indexer[lowRange] / 2)
        self.activeSamples[i] = []
        self.pulseIndices[i] = []
        for group in groups:
            for dataPoint in group:
                self.activeSamples[i].append(dataPoint[1])
            self.pulseIndices[i].append(len(self.activeSamples[i]))

    def averageMaxSamples(self, lowRange):
        i = int(self.indexer[lowRange] / 2)
        data = np.array(self.activeSamples[i])
        return np.average(data)

    """
    Calculates the linear function to map the ADC samples to a motor signal such that low range produces no motor motion
    and high range produces the maximum motor motion.
    """
    def getLinearMotorResponseFunc(self, neutralPos, maxPos, fname):
        # Get the average pulse value at the extents of desired response
        self.vLin[0] = self.averageMaxSamples(True)
        self.vLin[1] = self.averageMaxSamples(False)
        self.linResponseParams[0] = (maxPos - neutralPos) / (self.vLin[1] - self.vLin[0])
        self.linResponseParams[1] = (neutralPos * self.vLin[1] - maxPos * self.vLin[0]) / (self.vLin[1] - self.vLin[0])
        print("Linear response parameters")
        print("m: " + str(self.linResponseParams[0]))
        print("b: " + str(self.linResponseParams[1]))
        with open(fname + ".txt", "w") as file:
            file.write("\tLinear Motor Response\n")
            file.write("Expected range of ADC samples: " + str(self.vLin[0]) + " - " + str(self.vLin[1]) + "\n")
            file.write("M = " + str(self.linResponseParams[0]) + "v + " + str(self.linResponseParams[1]) + "\n")

    """
    Creates a new (i, d, v) data point.
    Assumes that the user has the set up with the correct current (i) and distance from nerve center (d).
    Runs data collection and analysis software to determine the corresponding v value, then adds the data point to the
    dataset.
    """
    def newidvDataPoint(self, i, d):
        self.sampleUc(True)
        self.groupMaxSamples(True)

