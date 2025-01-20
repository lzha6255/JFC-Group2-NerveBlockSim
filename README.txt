Instructions:

1. CHECK PREPROCESSOR DIRECTIVES
If using the actual stimuplex, remove or comment out the macro SIM from stimuplex_simulator.ino, and ensure that the macro OUTPUT_ONLY is defined. This stops the Arduino from simulating the pulses of the stimuplex out of DP5, and also prevents the Arduino from sending any dummy optocoupler input data.

2. SET UP MICROCONTROLLER
Upload stimuplex_simulator.ino to the Arduino Uno. Ensure that there is serial connection to the PC.

3. SET UP PC
Ensure that there are two directories named "figures" and "datasets" in the same directory as test.py and MaterialTester.py. Run the program test.py. Follow the directives in the console application.