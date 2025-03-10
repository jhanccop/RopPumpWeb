import json
import base64

class LoRaPacketDecoder:
    def __init__(self):
        self.decoded_data = {}
    
    def decode_base64(self, payload):
        """Decodifica un payload en base64 a bytes."""
        try:
            return base64.b64decode(payload)
        except Exception as e:
            raise ValueError(f"Error decodificando base64: {str(e)}")
    
    def bytes_to_int(self, bytes_data):
        """Convierte bytes a entero."""
        return int.from_bytes(bytes_data, byteorder='big')
    
    def decode_float(self, bytes_data):
        """Decodifica float (asume 2 bytes, con un decimal)."""
        temp = self.bytes_to_int(bytes_data)
        return temp / 10.0
    
    def decode_int(self, bytes_data):
        """Decodifica int (asume 2 bytes, con un decimal)."""
        temp = self.bytes_to_int(bytes_data)
        return temp
    
    def decode_humidity(self, bytes_data):
        """Decodifica humedad (asume 1 byte, valor entero)."""
        return self.bytes_to_int(bytes_data)
    
    def decode_pressure(self, bytes_data):
        """Decodifica presión (asume 2 bytes, en hPa)."""
        return self.bytes_to_int(bytes_data)
    
    def decode_packet(self, payload):
        """Decodifica un paquete LoRa completo."""
        # Decodificar base64 si es necesario
        if isinstance(payload, str):
            raw_bytes = self.decode_base64(payload)
        else:
            raw_bytes = payload

        print(payload, raw_bytes)
        
        # Verificar longitud mínima
        if len(raw_bytes) < 8:
            raise ValueError("Paquete demasiado corto")
        
        # Decodificar los campos
        # Asumimos un formato: 2 bytes temp, 1 byte hum, 2 bytes pressure
        self.decoded_data = {
            'spm': self.decode_float(raw_bytes[0:2]),
            'fillPump': self.decode_int(raw_bytes[2:4]),
            'sLength': self.decode_float(raw_bytes[4:6]),
            'vBat': self.decode_float(raw_bytes[6:8]),
            'status': self.decode_humidity(raw_bytes[8:9]),
        }
        
        return self.decoded_data
    
    def to_json(self):
        """Convierte los datos decodificados a JSON."""
        return json.dumps(self.decoded_data, indent=2)

# Ejemplo de uso
def main():
    # Ejemplo de payload en base64 (temperatura=25.5, humedad=60%, presión=1013)
    # Los valores están codificados como:
    # Temp: 255 (25.5°C) -> 0x00FF
    # Hum: 60 (60%) -> 0x3C
    # Presión: 1013 (hPa) -> 0x03F5
    #example_payload = "AP88D/U="
    example_payload = "AGwAAAAEAC0B"
    decoder = LoRaPacketDecoder()
    
    try:
        decoded = decoder.decode_packet(example_payload)
        print("Datos decodificados:")
        print(decoder.to_json())
    except Exception as e:
        print(f"Error decodificando: {str(e)}")

if __name__ == "__main__":
    main()