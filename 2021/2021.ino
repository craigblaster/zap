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
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int analogOutPin = 9; // Analog output pin that the LED is attached to
const int maxSamples = 1000;
// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led = 13;
short wave [maxSamples]; //place to store a waveform


short sensorValue = 0;        // value read from the pot
short maxValue = 0;
unsigned long nowTime = 0;
unsigned long lastTime = 0;
int LEDValue = false;

long unsigned int total = 0;
long unsigned int sampleCounter = 0;

void setup() {
  // initialize serial communications at 14400 bps:
  Serial1.begin(14400); 
  Serial.begin(14400); 
  pinMode(led, OUTPUT);     
  Serial1.println("average, rate, max value");   
}

void loop() {
  
  nowTime = millis();
  // read the analog in value:
  sensorValue = analogRead(analogInPin);            
  wave[sampleCounter] = sensorValue;

  sampleCounter++;
  total += sensorValue;
  if(sensorValue > maxValue)
  {
    maxValue = sensorValue;
  }

  if (sampleCounter > maxSamples)
  {
    digitalWrite(led, LOW);
  
    // print the results to the serial monitor:
    
    //Serial1.print("average = " );    
    Serial1.print(total / sampleCounter);      
    //Serial1.print(", rate = " );                       
    Serial1.print(",");
    Serial1.print(sampleCounter);  
    //Serial1.print(", maxValue = " );                       
    Serial1.print(",");    
    Serial1.println(maxValue);   
    
    for (unsigned int i=0;i<maxSamples;i++)
    {
      Serial1.print(wave[i]);   
      Serial1.print(",");    
    }
    Serial1.println();
    
//    
//    if(LEDValue == 1)
//    {
//      LEDValue = 0;
//      digitalWrite(led, LOW);
//    }
//    else
//    {
//      LEDValue = 1;
//      digitalWrite(led, HIGH);
//    }
//  
    digitalWrite(led, HIGH);
    total=0;
    sampleCounter=0;  
    maxValue = 0;
    lastTime = millis();
  }  
}
