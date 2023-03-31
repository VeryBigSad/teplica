import datetime
import socket
import sqlite3
import statistics

import matplotlib.pyplot as plt

from constants import MAX_TEMP, MIN_TEMP, MODE_AUTOMATIC, MODE_MANUAL
from manual_settings import ManualSettings
from protocol import Protocol


class Server:
    """
    Procesess requests from arduinos using protocol.
    """

    instance = None

    def __init__(self, hostname, port, database_file):
        """Creates a Server object

        Args:
            hostname (str): ip of what ip to accept
            port (int): port of where to start the server
        """
        self.hostname = hostname
        self.port = port

        self.database_file = database_file

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))

        self.mode = MODE_AUTOMATIC

        self.temperature_outside = None
        self.temperature_inside = None
        self.ventil_power = None
        self.is_servo_on = None

        self.set_settings()
        if Server.instance is not None:
            raise ValueError(
                "Warning! 2 or more instances of Server running. This is not allowed!"
            )
        Server.instance = self

    def get_mode(self) -> str:
        return self.mode

    def set_mode(self, new_mode: str) -> None:
        self.mode = new_mode

    @classmethod
    def get_instance(cls):
        return cls.instance

    def start_listening(self) -> None:
        """Make the socket start listening"""
        print(f"Слушаю на {self.port} порту")
        self.socket.listen(10)

    def wait_for_client(self) -> tuple:
        """Waiting for incoming connections"""
        return self.socket.accept()

    def set_settings(self, is_servo_on: bool = None, ventil_power: int = None) -> None:
        if is_servo_on is None:
            is_servo_on = self.is_servo_on
        if ventil_power is None:
            ventil_power = self.ventil_power

        self.settings = ManualSettings(is_servo_on, ventil_power)

    def get_data_to_respond(self) -> bytes:
        """Returns how much to turn on/off servo/ventilator"""

        temp_inside = self.get_inside_temp()
        temp_outside = self.get_outside_temp()
        if temp_inside is None or temp_outside is None:
            return b"0;0"

        if self.mode == MODE_MANUAL:
            # just do what we are said to do in such case
            data = bytes(f"{'1' if self.settings.is_servo_on else '0'};{self.settings.ventil_power}", encoding='ascii')
            print(f"servo: {self.settings.is_servo_on}, ventil power: {self.settings.ventil_power}%")
            return data

        if temp_inside is None or temp_outside is None:
            return b"0;0"
        if temp_inside > MIN_TEMP and temp_inside < MAX_TEMP:
            # норм температура
            print("norm")
            return b"0;0"
        if temp_inside > temp_outside:
            # температура внутри выше температуры снаружи, открываем форточку
            print("открыл форточку")
            return b"1;0"
        else:
            # температура внутри ниже, чем снаружи, включаем вентилятор
            ventil_power = int(self.get_ventil_power())
            print(f"включил вентилятор на {ventil_power}%")
            return b"0;" + bytes(str(ventil_power), encoding='ascii')

    def process_request(self, clientsocket, addr) -> None:
        """Processes any request coming from 2 of the arduinos"""
        data = clientsocket.recv(1024).decode()
        protocol = Protocol.get_protocol_from_data(data)
        self.record_protocol(protocol)
        if protocol.arduino_id == 1:
            # return because no reason to continue or answer anything,
            # this module doesn't have antyhing attached
            self.temperature_outside = protocol.temperature
            print(f"Температура на улице: {self.temperature_outside}")
            return
        self.temperature_inside = protocol.temperature
        self.is_servo_on = protocol.is_servo_on
        self.ventil_power = protocol.ventil_power
        print(f"Температура внутри: {self.temperature_inside}")
        data = self.get_data_to_respond()
        clientsocket.sendall(data)

    def record_protocol(self, protocol: Protocol) -> None:
        print("recorded: ", protocol)
        conn = sqlite3.connect(self.database_file)
        conn.execute("INSERT INTO temperature_readings (temperature, arduino_id, created_at) VALUES (?, ?, ?)",
                     (protocol.temperature, protocol.arduino_id, datetime.datetime.now()))
        conn.commit()

    def create_picture(self, name):
        # Retrieve the last 5 minutes of temperature readings from the two arduinos
        five_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
        conn = sqlite3.connect(self.database_file)
        query = "SELECT temperature, arduino_id, created_at FROM temperature_readings WHERE created_at >= ? AND arduino_id <= 2"
        result = conn.execute(query, (five_minutes_ago,)).fetchall()

        # Separate the data by arduino ID
        arduino1_data = []
        arduino2_data = []
        for row in result:
            if row[1] == 1:
                arduino1_data.append(row)
            elif row[1] == 2:
                arduino2_data.append(row)

        # Create a plot of the data
        x1, y1 = [row[2] for row in arduino1_data], [row[0] for row in arduino1_data]
        x2, y2 = [row[2] for row in arduino2_data], [row[0] for row in arduino2_data]
        plt.figure(figsize=(20,7))
        plt.plot(x1, y1, label='На улице')
        plt.plot(x2, y2, label='Внутри')
        plt.xlabel('Время')
        plt.locator_params(axis='x', nbins=10)
        plt.xticks(rotation='vertical')
        plt.margins(0.2)
        plt.ylabel('Температура')
        plt.legend()

        # Save the plot to a file
        plt.savefig(f'{name}.png')
        plt.clf()
    
    def get_outside_temp(self):
        conn = sqlite3.connect(self.database_file)
        eight_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds=8)
        query = "SELECT temperature FROM temperature_readings WHERE created_at >= ? and arduino_id = 1"
        result = conn.execute(query, (eight_seconds_ago,)).fetchall()
        conn.close()
        temperatures = [row[0] for row in result]
        try:
            median_temperature = statistics.median(temperatures)
        except statistics.StatisticsError:
            return None
        return round(median_temperature, 2)

    def get_inside_temp(self):
        conn = sqlite3.connect(self.database_file)
        eight_seconds_ago = datetime.datetime.now() - datetime.timedelta(seconds=8)
        query = "SELECT temperature FROM temperature_readings WHERE created_at >= ? and arduino_id = 2"
        result = conn.execute(query, (eight_seconds_ago,)).fetchall()
        conn.close()
        temperatures = [row[0] for row in result]
        try:
            median_temperature = statistics.median(temperatures)
        except statistics.StatisticsError:
            return None
        return round(median_temperature, 2)

    def get_ventil_power(self):
        thing = max(min(10, self.temperature_outside - self.temperature_inside) * 10, 0)
        if thing < 50:
            return 50
        return thing
