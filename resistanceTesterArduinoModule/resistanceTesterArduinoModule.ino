void setup() {
  // put your setup code here, to run once:
  pinMode(5, OUTPUT);
  pinMode(A5, INPUT);
  Serial.begin(9600);
  digitalWrite(5, HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(analogRead(A5));
  delay(500);
}
