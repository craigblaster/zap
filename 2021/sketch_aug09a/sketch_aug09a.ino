/*
  Analog input, analog output, serial output
 
 Reads an analog input pin, maps the result to a range from 0 to 255
 and uses the result to set the pulsewidth modulation (PWM) of an output pin.
 Also prints the results to the serial monitor.
 
 The circuit:
 * potentiometer connected to analog pin 0.
   Center pin of the potentiometer goes to the analog pin.
   side pins of the potentiometer go to +5V and ground
 * LED connected from digital pin 9 to ground
 
 created 29 Dec. 2008
 modified 9 Apr 2012
 by Tom Igoe
 
 This example code is in the public domain.
 
 */

// These constants won't change.  They're used to give names
// to the pins used:
const int analogInPin_current = A0;  // Analog input pin that the current clamp is attached to
const int analogInPin_voltage = A1;  // Analog input pin that the voltage transformer is attached to
const int analogOutPin = 9; // Analog output pin that the LED is attached to
const int maxSamples = 500;
// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led = 13;
short samples_current [maxSamples]; //place to store samples of current
short samples_voltage [maxSamples]; //place to store samples of voltage


short sensorValue = 0;        // value read from the pot
short maxValue = 0;
unsigned long nowTime = 0;
unsigned long lastTime = 0;
int LEDValue = false;

long unsigned int total = 0;
long unsigned int sampleCounter = 0;

void setup() {
  // initialize serial communications at 14400 bps:
  Serial1.begin(115200); // for sending to rpi
  Serial.begin(14400); // unused
  pinMode(led, OUTPUT);     
  Serial1.println("average, rate, max value");   
}

void loop() {
  
  //delayMicroseconds(1);
  nowTime = millis();
  // get a sample of current and voltage
  // do it close together so that we can measure phase     
  samples_current[sampleCounter] = analogRead(analogInPin_current);
  samples_voltage[sampleCounter] = analogRead(analogInPin_voltage);
  sampleCounter++;

  if (sampleCounter > maxSamples)
  {
    // turn the LED off to indicate sampling
    digitalWrite(led, LOW);
  
    // print the results to the serial monitor:
    // current
    Serial1.print("[[");   
    Serial1.print(samples_current[0]);   
    for (unsigned int i=1;i<maxSamples;i++)
    {
      Serial1.print(",");
      Serial1.print(samples_current[i]);   
    }
    Serial1.print("],[");
    
    // voltage
    Serial1.print(samples_voltage[0]);
    for (unsigned int i=1;i<maxSamples;i++)
    {
      Serial1.print(",");  
      Serial1.print(samples_voltage[i]);   
    }
    Serial1.println("]]");
    
    // turn the LED on to indicate sleeping
    digitalWrite(led, HIGH);
    total=0;
    sampleCounter=0;  
    maxValue = 0;
    lastTime = millis();
    delay(50);
  }  
}
