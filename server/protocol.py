class Protocol:
    def __init__(self, arduino_id, is_servo_on, ventil_power, temperature):
        self.arduino_id = int(arduino_id)
        # TODO: probably bug here, idk yet
        self.is_servo_on = is_servo_on == "1" 
        self.ventil_power = float(ventil_power)
        self.temperature = float(temperature)

    @classmethod
    def get_protocol_from_data(cls, data):
        print()
        arduino_id, is_servo_on, ventil_power, temperature = data.split(";")
        return cls(arduino_id, is_servo_on, ventil_power, temperature)

    def __str__(self):
        return f"Arduino id: {self.arduino_id}, servo: {self.is_servo_on}, ventil_power: {self.ventil_power}, temperature: {self.temperature}"


