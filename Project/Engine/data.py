import time
import json
from flask import current_app
import os
class Data:
    def __init__(self):
        self._history = {}
        self._filename = os.path.join("Project", "Engine", "log", "data.json")
    def addData(self, key, value):
        if key not in self._history:
            self._history[key] = []
        self._history[key].append((time.time(), value))
        
        if current_app:
            producer = current_app.config.get('KAFKA_PRODUCER')
            kafka_topic = current_app.config.get('KAFKA_TOPICS', {}).get(key)
            
            if producer and kafka_topic:
                # Transforme les données en Influx Line Protocol
                formatted_message = self.to_influx_line_protocol(key, value, time.time())
                # Envoie le message brut au topic Kafka
                producer.send(kafka_topic, value=formatted_message.encode('utf-8'))

    def save(self):
        f = open(self._filename, "w")
        toWrite = json.dumps(self._history)
        f.write(toWrite)
        f.close()

    def getHistory(self):
        return self._history
    
    @staticmethod
    def to_influx_line_protocol(key, value, timestamp):
        """
        Convertit les données en Influx Line Protocol.
        - key : nom de la mesure
        - value : dictionnaire contenant les données
        - timestamp : timestamp en secondes (sera converti en nanosecondes)
        """
        # Convertir les champs booléens en true/false pour InfluxDB
        fields = ",".join(
            [
                f"{k}={str(v).lower() if isinstance(v, bool) else v}"
                for k, v in value.items()
                if isinstance(v, (int, float, bool))
            ]
        )
        # Inclure les champs string comme tags
        tags = ",".join([f"{k}={v}" for k, v in value.items() if isinstance(v, str)])
        # Retourner le protocole Influx Line
        return f"{key},{tags} {fields} {int(timestamp * 1e9)}"

