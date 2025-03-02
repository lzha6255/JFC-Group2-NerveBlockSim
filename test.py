import MaterialTester
import ResistanceTester

def sampleAndPlot():
    print("Please set your HNS12 Stimuplex device's current to the lower limit of muscle response (" + str(
        tester.stimRanges[0]) + " mA).")
    print("Press enter when the device has been set up and is running to begin sampling.")
    input()
    print("Sampling...")
    tester.sampleUc(True)
    print("Done.")

    tester.plotData(True, "figures\\" + matName + "Low.png", "OSIM " + matName + " low range (" + str(tester.stimRanges[0]) + " mA) response", "Time (ns)", "A0 sample")

    print("Please set your HNS12 Stimuplex device's current to the upper limit of muscle response (" + str(
        tester.stimRanges[1]) + " mA).")
    print("Press enter when the device has been set up and is running to begin sampling.")
    input()
    print("Sampling...")
    tester.sampleUc(False)
    print("Done.")

    tester.plotData(False, "figures\\" + matName + "High.png", "OSIM " + matName + " high range (" + str(tester.stimRanges[1]) + " mA) response", "Time (ns)", "A0 sample")

def setStimLims():
    print("Please enter the lower limit of stimuplex current in mA:")
    low = float(input())
    print("Please enter the upper limit of stimuplex current in mA:")
    hi = float(input())
    tester.stimRanges = [low, hi]

def dataAnalysis():
    # tester.aboveAveragePulseSamples(True)
    tester.groupMaxSamples(True)
    tester.plotActiveSamples(True, "figures\\" + matName + "_low_range_pulses.png", matName + " pulse datapoints (low range)", "Sample Number", "A0 Sample")
    tester.groupMaxSamples(False)
    tester.plotActiveSamples(False, "figures\\" + matName + "_high_range_pulses.png", matName + " pulse datapoints (high range)", "Sample Number", "A0 Sample")
    print("Average pulse sample value low range: " + str(tester.averageMaxSamples(True)))
    print("Average pulse sample value high range: " + str(tester.averageMaxSamples(False)))
    tester.getLinearMotorResponseFunc(16, 0, "parameters\\" + matName + "_lin_response_func")

def saveData():
    fname = "datasets\\" + matName
    tester.saveData(fname)
    print("Data saved.")

def setSampleTime():
    print("Please enter the sample time in seconds:")
    t = input()
    tester.sampleTimeNs = float(t) * 1e9

def setStimFreq():
    print("Please enter the stimuplex pulse frequency in Hz:")
    f = input()
    tester.stimFreq = int(f)

def testResistance():
    print("Please ensure that the circuit and microcontroller are set up to test the material's resistance.")
    print("Enter stability limit in seconds when ready:")
    stabilityLimit = int(input())
    print("Enter stability window in adc sample value:")
    stabilityWindow = int(input())
    rTester.sample(True, stabilityLimit, stabilityWindow)
    print("Enter the resistance in series with the test material in ohms:")
    r = float(input())
    rTester.ADCRead2Resistance(r)
    rTester.plotResistance("figures\\" + matName + " resistance test", title=matName + " resistance test")
    print("Enter file name to save resistance testing data:")
    fname = input()
    rTester.saveData(fname)

def findPlanarFunctions():
    tester.idvData = []
    print("Please set your HNS12 Stimuplex device's current to the lower limit of muscle response (" + str(tester.stimRanges[0]) + " mA).")
    print("Please also position the anode (needle tip) to be as close to the cathode as possible without making direct contact.")
    print("Press enter to begin sampling.")
    input()
    tester.newidvDataPoint(tester.stimRanges[0], 0)
    print("Please set your HNS12 Stimuplex device's current to the upper limit of muscle response (" + str(tester.stimRanges[1]) + " mA).")
    print("Please also position the anode (needle tip) to be as close to the cathode as possible without making direct contact.")
    print("Press enter to begin sampling.")
    input()
    tester.newidvDataPoint(tester.stimRanges[1], 0)
    print("Please set your HNS12 Stimuplex device's current to the lower limit of muscle response (" + str(tester.stimRanges[0]) + " mA).")
    print("Please also position the anode (needle tip) to be roughly 1 cm away from the cathode.")
    print("Press enter to begin sampling.")
    input()
    tester.newidvDataPoint(tester.stimRanges[0], 10)
    tester.calcPlanarVFunc("parameters\\" + matName + "_V_function")

print("Hi, welcome to the Optocoupler-Stimuplex Interface Material Test and Calibration Framework (OSIMTCF).")
print("This program will sample data from the optocoupler-stimuplex-material sensing loop, and provide plots/analysis of collected datasets.")
print("Please provide the name of the material to be tested: ")
matName = input()
tester = MaterialTester.MaterialTester(matName)
rTester = ResistanceTester.ResistanceTester()

menuOptions = ["Sample and plot",
               "Data analysis",
               "Set stimuplex limits",
               "Save data",
               "Set sampling time",
               "Set stimuplex frequency",
               "Conduct resistance test",
               "Find f(i, d) and motor signal function g(f)",
               "Exit"]
while True:
    print("Enter one of the following options:")
    for i in range(0, len(menuOptions)):
        print(str(i + 1) + ". " + menuOptions[i])
    menuSelection = input()
    try:
        menuSelection = int(menuSelection)
    except:
        print("Please enter a numerical value.")
        continue
    if menuSelection == len(menuOptions):
        break
    elif menuSelection == 1:
        sampleAndPlot()
    elif menuSelection == 2:
        dataAnalysis()
    elif menuSelection == 3:
        setStimLims()
    elif menuSelection == 4:
        saveData()
    elif menuSelection == 5:
        setSampleTime()
    elif menuSelection == 6:
        setStimFreq()
    elif menuSelection == 7:
        testResistance()
    elif menuSelection == 8:
        findPlanarFunctions()
