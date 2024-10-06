from boot import do_connect
from microdot import Microdot, send_file
import neopixel
import machine

# Conecta el dispositivo a Wi-Fi utilizando la función do_connect
do_connect()

# Inicializa la aplicación web Microdot
app = Microdot()

# Configura los pines para los LEDs en los pines GPIO 32, 33 y 25
led1 = machine.Pin(32, machine.Pin.OUT)
led2 = machine.Pin(33, machine.Pin.OUT)
led3 = machine.Pin(25, machine.Pin.OUT)

# Configura una tira NeoPixel de 8 LEDs en el pin GPIO 27
np = neopixel.NeoPixel(machine.Pin(27), 8)

# Ruta principal que sirve el archivo index.html como la página de inicio
@app.route('/')
def index(request):
    try:
        return send_file('index.html')
    except OSError:
        return 'Archivo index.html no encontrado', 404

# Ruta que sirve archivos estáticos (por ejemplo, CSS, imágenes, etc.)
@app.route('/<dir>/<file>')
def static_file(request, dir, file):
    try:
        return send_file(f"/{dir}/{file}")
    except OSError:
        return f'Archivo {file} no encontrado en {dir}', 404

# Ruta que permite controlar el encendido y apagado de los LEDs
@app.route('/led')
def led_control(request):
    try:
        led_num = int(request.args.get('led'))
        state = request.args.get('state') == 'true'

        if led_num not in [1, 2, 3]:
            return 'El número de LED debe ser 1, 2 o 3', 400

        # Selecciona el LED correspondiente
        led = [led1, led2, led3][led_num - 1]

        # Controla el estado del LED
        led.value(1 if state else 0)

        return f'LED {led_num} {"encendido" if state else "apagado"}'

    except (ValueError, IndexError):
        return 'Entrada no válida', 400

# Ruta que permite controlar el color de la tira LED NeoPixel
@app.route('/color')
def color_control(request):
    try:
        r = int(request.args.get('r', 0))
        g = int(request.args.get('g', 0))
        b = int(request.args.get('b', 0))

        if not all(0 <= val <= 255 for val in (r, g, b)):
            return 'Los valores RGB deben estar entre 0 y 255', 400

        np.fill((r, g, b))
        np.write()

        return f'Color establecido a R:{r}, G:{g}, B:{b}'

    except ValueError:
        return 'Valores RGB no válidos', 400

# Ejecuta el servidor en el puerto 80
app.run(port=80)

