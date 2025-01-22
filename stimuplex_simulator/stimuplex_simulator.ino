// # define SIM
# define OUTPUT_ONLY

#ifdef SIM
int stimuplexPulsePin = 5;
bool stimuplexPulseOn = false;

unsigned long lastPulseSwitch = 0;
unsigned long timeSinceSwitch = 0;
unsigned long onTimeUs = 1000;
unsigned long offTimeUs = 499000;

int optoInputPin = A1;
int optoInputV = 0;
#endif

int optoOutputV = 0;
int optoOutputPin = A0;

bool start = false;

void setup() {
  // put your setup code here, to run once:
  #ifdef SIM
  pinMode(stimuplexPulsePin, OUTPUT);
  pinMode(optoInputPin, INPUT);
  lastPulseSwitch = micros();
  #endif
  pinMode(optoOutputPin, INPUT);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (start)
  {
    #ifdef SIM
    timeSinceSwitch = micros() - lastPulseSwitch;
    // Switching logic for simulated stimuplex pulse
    if (stimuplexPulseOn && timeSinceSwitch > onTimeUs)
    {
      digitalWrite(stimuplexPulsePin, LOW);
      lastPulseSwitch = micros();
      stimuplexPulseOn = false;
    }
    else if (timeSinceSwitch > offTimeUs)
    {
      digitalWrite(stimuplexPulsePin, HIGH);
      lastPulseSwitch = micros();
      stimuplexPulseOn = true;
    }

    // Send the reading for optocoupler input
    #ifndef OUTPUT_ONLY
    optoInputV = analogRead(optoInputPin);
    Serial.println(optoInputV);
    #endif
    #endif
    #ifndef SIM
    #ifndef OUTPUT_ONLY
    // Dummy value as the optocoupler input is decoupled from the uC and can not be read meaningfully
    Serial.println(0);
    #endif
    #endif
    optoOutputV = analogRead(optoOutputPin);
    Serial.println(optoOutputV);

    // Check for stop signal
    if (Serial.available())
    {
      int incomingByte = Serial.read();
      if (incomingByte == 1)
        start = false;
    }
  }
  else
  {
    if (Serial.available() > 0)
    {
      int incomingByte = Serial.read();
      if (incomingByte == 1)
      {
        start = true;
        analogRead(optoOutputPin);
        delay(100);
      }
    }
  }
}
