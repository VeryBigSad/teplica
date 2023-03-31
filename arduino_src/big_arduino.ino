#include <WiFi.h>
#include <ESP32Servo.h>
#include <stdio.h>  // Для printf
#include <string.h> // Для strtok

const char* ssid = "dreamteam";
const char* password = "79397939";
const char* server_ip = "10.10.10.10";

const int Port = 34;
const int servoPort = 2; //нужен 2 или 1?. Разобраться с мусором
const int ledPin = 16; 
const int ledChannel = 5;
const int resolution = 8;
const int freq = 5000;
const float base = 2.55;

String esp_id = "2";
int is_servo_on = 0;
int is_ventil_on = 0;
int counter = 0;
String tok;


WiFiClient client;
Servo servo;
String data;
int c = 0;



void setup() {
  ESP32PWM::allocateTimer(0);
  servo.setPeriodHertz(50);
  Serial.begin(9600);
  pinMode(16, OUTPUT);
  servo.attach(servoPort, 500, 2400);
  servo.write(0);
  delay(1000);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }  
  ledcSetup(ledChannel, freq, resolution);
  ledcAttachPin(ledPin, ledChannel);
}

void loop() {
  int analogSignal = analogRead(Port);
  String temperature = String(get_temperature(analogSignal));

  data = esp_id + ";" + String(is_servo_on) + ";" + String(is_ventil_on) + ";" + temperature;
  send_data(data);
  delay(100);

}


float get_temperature(float signal){
  return signal / 10 - 273;
}

bool connect_to(){
  Serial.print("Подключение к ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  return true;
}


void send_data(String info) {
  if (!client.connect(server_ip, 35353)) {
    Serial.println("Connection failed");
  } 

  client.println(info);

  Serial.println("Ждем ответ от сервера");
  while (client.connected()) {
    if ( client.available() ) {
      String line = client.readStringUntil('\n');
      tok = line.substring(0, line.indexOf(';'));
      int turn_on = tok.toInt();
      tok = line.substring(line.indexOf(';')+1);
      int ventil_ON = tok.toInt();
      Serial.println("Значения серво:" + String(turn_on));
      Serial.println("Мощность вентилятора:" + String(ventil_ON));
      servo_settings(turn_on);
      ventil_settings(ventil_ON);
      c += 1;
  }
    if (c == 1){
      c = 0;
      break;
    }
  }
}

void servo_settings(int turn_on){
  if (turn_on == 1 & is_servo_on == 0){
    servo.write(25);
    is_servo_on = 1;
  } 
  else if (turn_on == 0 & is_servo_on == 1){
    servo.write(135);
    is_servo_on = 0;
  }
}

void ventil_settings(int turn_on) {
  ledcWrite(ledChannel, int(turn_on*base));
  is_ventil_on = turn_on;
}