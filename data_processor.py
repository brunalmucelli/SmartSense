import psycopg2
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Configurações do banco de dados
DATABASE = {
    "dbname": "sensor_data",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5432
}

class DataProcessor:
    def __init__(self, mqtt_broker, mqtt_port, database_config):
        """
        Inicializa o processador de dados.

        :param mqtt_broker: Endereço do broker MQTT.
        :param mqtt_port: Porta do broker MQTT.
        :param database_config: Configurações do banco de dados.
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.database_config = database_config
        self.client = mqtt.Client()
        self.sensors_last_seen = {}  # Para monitorar inatividade dos sensores

    def connect_db(self):
        """Conecta ao banco de dados PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.database_config)
            conn.autocommit = True
            return conn
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def persist_data(self, machine_id, sensor_id, timestamp, value):
        """Persiste os dados do sensor no banco de dados."""
        conn = self.connect_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sensor_metrics (time, machine_id, sensor_id, value)
                        VALUES (%s, %s, %s, %s)
                    """, (timestamp, machine_id, sensor_id, value))
                    print(f"Dado persistido: {machine_id}, {sensor_id}, {timestamp}, {value}")
            except psycopg2.Error as e:
                print(f"Erro ao persistir dado: {e}")
            finally:
                conn.close()

    def persist_alarm(self, machine_id, sensor_id, alarm_type, details):
        """Persiste alarmes no banco de dados."""
        conn = self.connect_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO alarms (time, machine_id, sensor_id, alarm_type, details)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (datetime.utcnow(), machine_id, sensor_id, alarm_type, details))
                    print(f"Alarme persistido: {machine_id}, {sensor_id}, {alarm_type}, {details}")
            except psycopg2.Error as e:
                print(f"Erro ao persistir alarme: {e}")
            finally:
                conn.close()

    def handle_message(self, client, userdata, msg):
        try:
            print(f"Tópico recebido: {msg.topic}, Mensagem: {msg.payload.decode()}")
            topic_parts = msg.topic.split("/")

            # Verifica se o tópico é "/sensor_monitors"
            if msg.topic == "/sensor_monitors":
                data = json.loads(msg.payload)
                machine_id = data["machine_id"]
                sensors = data["sensors"]
                print(f"Informações recebidas de sensores: {sensors}")
                # Opcional: Persistir informações gerais sobre os sensores no banco de dados, se necessário
                return

            # Verifica se o tópico tem o formato esperado para dados de sensores
            if len(topic_parts) < 4 or topic_parts[1] != "sensors":
                print(f"Tópico inválido: {msg.topic}")
                return

            # Processa dados do sensor
            machine_id = topic_parts[2]
            sensor_id = topic_parts[3]
            data = json.loads(msg.payload)
            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            value = data["value"]

            # Persistir o dado no banco de dados
            self.persist_data(machine_id, sensor_id, timestamp, value)

            # Atualizar o último horário visto do sensor
            self.sensors_last_seen[(machine_id, sensor_id)] = datetime.utcnow()
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
   

    def check_inactive_sensors(self):
        """Verifica sensores inativos e gera alarmes."""
        now = datetime.utcnow()
        for (machine_id, sensor_id), last_seen in self.sensors_last_seen.items():
            # Considerar inativo após 10 períodos (exemplo: 10 segundos * 10 períodos)
            inactivity_threshold = 10 * 10
            if (now - last_seen).total_seconds() > inactivity_threshold:
                self.persist_alarm(
                    machine_id,
                    sensor_id,
                    "inactive",
                    f"Sensor {sensor_id} está inativo há mais de {inactivity_threshold} segundos."
                )

    def start(self):
        """Inicia o processador de dados."""
        self.client.on_message = self.handle_message
        self.client.connect(self.mqtt_broker, self.mqtt_port)
        self.client.subscribe("/sensor_monitors")
        self.client.subscribe("/sensors/+/+")
        self.client.loop_start()

        try:
            while True:
                self.check_inactive_sensors()
                time.sleep(10)  # Verificar sensores inativos a cada 10 segundos
        except KeyboardInterrupt:
            print("Encerrando o DataProcessor...")
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    # Configurações do MQTT Broker
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883

    # Instanciar e iniciar o DataProcessor
    processor = DataProcessor(
        mqtt_broker=MQTT_BROKER,
        mqtt_port=MQTT_PORT,
        database_config=DATABASE
    )
    processor.start()
