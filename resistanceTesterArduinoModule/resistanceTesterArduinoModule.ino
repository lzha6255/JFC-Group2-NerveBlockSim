int vccPin = 5;
int readPin = A5;

int interval = 500;
bool start = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(vccPin, OUTPUT);
  pinMode(readPin, INPUT);
  Serial.begin(9600);
  digitalWrite(vccPin, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (start)
  {
    Serial.println(analogRead(readPin));

    if (Serial.available() > 0)
    {
      int incomingByte = Serial.read();
      if (incomingByte == 1)
      {
        start = false;
        digitalWrite(vccPin, LOW);
      }
    }

    delay(interval);
  }
  else
  {
    if (Serial.available() > 0)
    {
      int incomingByte = Serial.read();
      if (incomingByte == 1)
      {
        start = true;
        digitalWrite(vccPin, HIGH);
      }
    }
  }
}
