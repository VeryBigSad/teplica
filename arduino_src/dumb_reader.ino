#include <WiFi.h>

const char* ssid = "dreamteam";
const char* password = "79397939";
const char* server_ip = "10.10.10.10";

WiFiClient client;

const int Port = 34;

String esp_id = "1";
int counter = 0;

void setup() {
  Serial.begin(9600);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }  

}

void loop() {

  int analogSignal = analogRead(Port);
  Serial.println(analogSignal);
  String temperature = String(get_temperature(analogSignal));

  String data = esp_id + ";" + "-1" + ";" + "-1" + ";" + temperature;
  send_data(data);
  delay(100);
}


float get_temperature(float signal){
  //float temperature = ((signal - 1730) / 1000) / 0.01;
  float temperature = signal / 10 - 270;
  //float temperature = (signal/10) - 273;
  Serial.print("Temperature:");
  Serial.println(temperature);

  return temperature;
}



void send_data(String info) {
  if (!client.connect(server_ip, 35353)) {
    Serial.println("Connection failed");
  } 
  client.println(info);
}