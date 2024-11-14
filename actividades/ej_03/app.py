from boot import do_connect
from microdot import Microdot, send_file, Response
from machine import Pin
import ds18x20
import onewire
import time

# Configuración del pin para el buzzer y el sensor de temperatura
buzzer_pin = Pin(14, Pin.OUT)  # Pin 14 controla el buzzer
ds_pin = Pin(19)               # Pin 19 conecta al sensor DS18B20
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))  # Inicializa el sensor
temperatureCelsius = 24  # Valor inicial de la temperatura

# Conecta a la red Wi-Fi
do_connect()

# Crea una instancia de la aplicación web
app = Microdot()

# Ruta principal que sirve el archivo index.html
@app.route('/')
async def index(request):
    try:
        return send_file('index.html')  # Envía el archivo si está disponible
    except OSError as e:
        return Response(body=f"Error: {e}", status_code=500)  # Error si no encuentra el archivo

# Ruta para servir archivos estáticos desde subdirectorios
@app.route('/<dir>/<file>')
async def static(request, dir, file):
    try:
        return send_file("/{}/{}".format(dir, file))  # Construye la ruta al archivo
    except OSError as e:
        return Response(body=f"Error: {e}", status_code=404)  # Error si el archivo no existe

# Ruta para leer la temperatura del sensor DS18B20
@app.route('/sensors/ds18b20/read')
async def temperature_measuring(request):
    global ds_sensor, temperatureCelsius
    try:
        roms = ds_sensor.scan()  # Busca dispositivos DS18B20
        if not roms:
            raise ValueError("No se encontraron dispositivos DS18B20")  # Error si no encuentra sensores
        
        ds_sensor.convert_temp()  # Inicia la conversión de temperatura
        time.sleep_ms(750)  # Pausa para asegurar que la conversión termine
        
        for rom in roms:
            temperatureCelsius = ds_sensor.read_temp(rom)  # Lee la temperatura
        
        json = {'temperature': temperatureCelsius}  # Prepara la respuesta JSON
        return json
    except (OSError, ValueError) as e:
        return Response(body=f"Error al leer la temperatura: {e}", status_code=500)  # Error de lectura

# Ruta para comparar el setpoint con la temperatura y controlar el buzzer
@app.route('/setpoint/set/<int:value>')
async def setpoint_calculation(request, value):
    global temperatureCelsius
    json = {}
    try:
        print("Calculando setpoint")  # Log de control
        if value >= temperatureCelsius:
            buzzer_pin.on()  # Activa el buzzer si el setpoint es mayor o igual
            json = {'buzzer': 'Encendido'}
        else:
            buzzer_pin.off()  # Apaga el buzzer si el setpoint es menor
            json = {'buzzer': 'Apagado'}
        
        return json  # Devuelve el estado del buzzer
    except Exception as e:
        return Response(body=f"Error al calcular el setpoint: {e}", status_code=500)  # Error genérico

# Ejecuta la aplicación en el puerto 80
app.run(port=80)
