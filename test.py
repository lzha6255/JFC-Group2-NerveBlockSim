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
    tester.plotActiveSamples(True, "figures\\" + matName + "ActiveSamplePlot.png", matName + " active samples low", "Sample Number", "A0 sample")

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
    rTester.sample(True, stabilityLimit)
    print("Enter the resistance in series with the test material in ohms:")
    r = float(input())
    rTester.ADCRead2Resistance(r)
    rTester.plotResistance("figures\\" + matName + " resistance test")
    print("Enter file name to save resistance testing data:")
    fname = input()
    rTester.saveData(fname)

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
