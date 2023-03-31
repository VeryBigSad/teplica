#include <WiFi.h>

// WiFi credentials
const char* ssid = "dreamteam";
const char* password = "79397939";

// Server IP and port
const char* server_ip = "10.10.10.10";
const int server_port = 35353;

// Analog pin for temperature sensor
const int temp_pin = 34;

// ID of the device
const String esp_id = "1";

// Number of times data has been sent to server
int counter = 0;

WiFiClient client;

void setup() {
  Serial.begin(9600);

  // Connect to WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }  
}

void loop() {
  // Read temperature sensor and convert to string
  int analogSignal = analogRead(temp_pin);
  Serial.println(analogSignal);
  String temperature = String(get_temperature(analogSignal));

  // Prepare data to send to server
  String data = esp_id + ";" + "-1" + ";" + "-1" + ";" + temperature;
  send_data(data);

  // Wait for some time before sending next data
  delay(3000);
}

// Convert analog signal to temperature in Celsius
float get_temperature(float signal){
  float temperature = signal / 10 - 273;
  Serial.print("Temperature:");
  Serial.println(temperature);

  return temperature;
}

// Send data to server
void send_data(String info) {
  if (!client.connect(server_ip, server_port)) {
    Serial.println("Connection failed");
  } 
  client.println(info);
}