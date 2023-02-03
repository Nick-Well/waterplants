// Pin assignments
const int analogInPin = A0;  // Pin for reading the soil moisture level
const int relayPin = 2;      // Pin for controlling the relay/pump

// Constants for timing
const int Hz = 2;           // Frequency of operation
const long serial = 9600 * Hz;   // Baud rate for serial communication
const long sekund = 1000 / Hz;   // Conversion factor for seconds to milliseconds
const long hour = 3600;      // Conversion factor for hours to seconds
const long restSensor = 2 * hour; // Delay after watering before checking soil moisture again
const long sensorDelay = 60;     // Delay between soil moisture checks
const float dl = 2.1 * sekund;   // Amount of water to dispense
const int amount = 2 * dl;       // Amount of water to dispense in milliseconds

// Variables
bool watered = false;        // Flag to keep track of watering status
int sensorValue = 0;        // Current soil moisture level
int outputValue = 0;        // Normalized soil moisture level (0-100)
int value = 0;              // Normalized soil moisture level (0-100)

void setup() {
  // Clock prescaler for power saving
  noInterrupts();
  CLKPR = _BV(CLKPCE);
  CLKPR = _BV(CLKPS0);
  interrupts();

  // Configure built-in LED and relay pin
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(relayPin, OUTPUT);

  // Initialize serial communication
  Serial.begin(serial);
  led(true);
  led(false);
}

void sleep(long time, bool water){
  // Initialize counter
  long i = 0;

  // Check if watering flag is true
  if(water){
    // Loop until counter reaches time
    while(i < time){
      show();
      delay(sekund);
      // Print current counter and target time
      Serial.print(i);
      Serial.print(" < ");
      Serial.println(time);
      // Increment counter
      i = i+1;
    }
    // Turn off LED
    led(false);
  }
  // If watering flag is false
  else {
    // Loop until counter reaches time
    while(i < time){
      show();
      // Turn on LED for half a second
      led(true);
      delay(sekund/2);
      // Turn off LED for half a second
      led(false);
      delay(sekund/2);
      // Print current counter and target time
      Serial.print(i);
      Serial.print(" < ");
      Serial.println(time);
      // Increment counter
      i = i+1;
    }
  } 
}

long show() {
  // Read the analog value from the moisture sensor
  sensorValue = analogRead(analogInPin);

  // Map the sensor value to a 0-100 range
  outputValue = map(sensorValue, 199, 499, 0, 100);

  // Print the sensor value and its mapped output
  Serial.print(sensorValue);
  Serial.print("\t output = ");
  Serial.println(outputValue);

  // Return the mapped output
  return outputValue;
}

void pump(float amount) {
  // Turn on the relay (to start the water pump)
  digitalWrite(relayPin, HIGH);

  // Wait for the specified amount of time
  delay(amount);

  // Turn off the relay (to stop the water pump)
  digitalWrite(relayPin, LOW);
}

void led(bool onOff) {
  // Turn the built-in LED on or off
  digitalWrite(LED_BUILTIN, onOff ? HIGH : LOW);
}

void loop() {
  // Get the mapped moisture sensor output
  value = show();

  // If the soil is too dry, start watering
  if (value > dry) {
    Serial.println("watering");
    pump(amount);
    Serial.println("done :)");
    led(true);
    sleep(restSensor, true);
  }
  // If the soil is not too dry, wait and check again later
  else {
    sleep(sensorDelay, false);
  }
}
}
