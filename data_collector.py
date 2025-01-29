import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import requests

class DataCollector:
    def __init__(self, machine_id, mqtt_broker, mqtt_port, sensors, publish_interval, api_key):
        """
        Inicializa o coletor de dados.

        :param machine_id: ID da máquina.
        :param mqtt_broker: Endereço do broker MQTT.
        :param mqtt_port: Porta do broker MQTT.
        :param sensors: Lista de sensores com informações sobre ID, tipo de dado e função de coleta.
        :param publish_interval: Intervalo de tempo para mensagens iniciais em segundos.
        :param api_key: Chave de acesso à API OpenWeather.
        """
        self.machine_id = machine_id
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.sensors = sensors
        self.publish_interval = publish_interval
        self.api_key = api_key
        self.client = mqtt.Client()

    def connect(self):
        """Conecta ao broker MQTT."""
        self.client.connect(self.mqtt_broker, self.mqtt_port)
        print(f"Conectado ao broker MQTT {self.mqtt_broker}:{self.mqtt_port}")

    def publish_sensor_data(self):
        """Coleta dados dos sensores e publica em tópicos MQTT."""
        for sensor in self.sensors:
            sensor_id = sensor["sensor_id"]
            data_type = sensor["data_type"]
            collect_func = sensor["collect_func"]

            # Coleta o valor do sensor
            value = collect_func()
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Cria a mensagem JSON
            message = {
                "timestamp": timestamp,
                "value": value
            }

            # Publica no tópico MQTT específico
            topic = f"/sensors/{self.machine_id}/{sensor_id}"
            self.client.publish(topic, json.dumps(message))
            print(f"Publicado no tópico {topic}: {message}")

    def publish_initial_message(self):
        """Publica a mensagem inicial com informações dos sensores monitorados."""
        sensors_info = [
            {
                "sensor_id": sensor["sensor_id"],
                "data_type": sensor["data_type"],
                "data_interval": sensor["data_interval"]
            }
            for sensor in self.sensors
        ]

        message = {
            "machine_id": self.machine_id,
            "sensors": sensors_info
        }

        self.client.publish("/sensor_monitors", json.dumps(message))
        print(f"Mensagem inicial publicada: {message}")

    def start(self):
        """Inicia o coletor de dados."""
        self.connect()
        self.client.loop_start()

        while True:
            # Publica a mensagem inicial
            self.publish_initial_message()

            # Publica os dados dos sensores
            self.publish_sensor_data()

            # Aguarda o intervalo configurado antes de repetir
            time.sleep(self.publish_interval)

# Função para obter dados da API OpenWeather
def get_weather_data(data_type, api_key, city="New York"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data_type == "temperature":
            return data["main"]["temp"]
        elif data_type == "humidity":
            return data["main"]["humidity"]
        elif data_type == "wind_speed":
            return data["wind"]["speed"]
    else:
        print(f"Erro ao acessar a API OpenWeather: {response.status_code}")
        return None

# Configuração dos sensores
api_key = "6e0e647bef1d3f51028a202f453d2124"
sensors = [
    {
        "sensor_id": "temp_01",
        "data_type": "temperature",
        "data_interval": 60,
        "collect_func": lambda: get_weather_data("temperature", api_key)
    },
    {
        "sensor_id": "hum_01",
        "data_type": "humidity",
        "data_interval": 60,
        "collect_func": lambda: get_weather_data("humidity", api_key)
    },
    {
        "sensor_id": "wind_01",
        "data_type": "wind_speed",
        "data_interval": 60,
        "collect_func": lambda: get_weather_data("wind_speed", api_key)
    }
]

# Instância e execução do DataCollector
if __name__ == "__main__":
    data_collector = DataCollector(
        machine_id="machine_001",
        mqtt_broker="localhost",
        mqtt_port=1883,
        sensors=sensors,
        publish_interval=60,
        api_key=api_key
    )
    data_collector.start()
