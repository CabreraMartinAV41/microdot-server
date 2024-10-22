from boot import do_connect  # Importa la función para conectar a Wi-Fi
from microdot import Microdot, send_file  # Importa el framework Microdot y función para enviar archivos
import neopixel  # Importa la biblioteca para controlar LEDs NeoPixel
import machine  # Importa módulos específicos del hardware

# Conecta el dispositivo a la red Wi-Fi usando la función definida en boot.py
do_connect()

# Inicializa la aplicación web usando Microdot
web_app = Microdot()

# Configura los pines GPIO para los LEDs simples
led_rojo = machine.Pin(32, machine.Pin.OUT)  # LED en GPIO 32
led_verde = machine.Pin(33, machine.Pin.OUT)  # LED en GPIO 33
led_azul = machine.Pin(25, machine.Pin.OUT)  # LED en GPIO 25

# Inicializa una tira de 8 LEDs NeoPixel conectada al GPIO 27
tiraled = neopixel.NeoPixel(machine.Pin(27), 8)

# Ruta principal: sirve el archivo index.html como página de inicio
@web_app.route('/')
def pagina_principal(request):
    try:
        return send_file('index.html')  # Envía el archivo index.html
    except OSError:
        return 'Archivo index.html no encontrado', 404  # Devuelve error 404 si no se encuentra el archivo

# Ruta para archivos estáticos como CSS o imágenes
@web_app.route('/<carpeta>/<archivo>')
def archivos_estaticos(request, carpeta, archivo):
    try:
        return send_file(f"/{carpeta}/{archivo}")  # Envía el archivo estático solicitado
    except OSError:
        return f'Archivo {archivo} no encontrado en {carpeta}', 404  # Error si no se encuentra

# Ruta para controlar el encendido/apagado de los LEDs simples
@web_app.route('/led')
def control_led(request):
    try:
        numero_led = int(request.args.get('led'))  # Obtiene el número del LED desde la URL
        estado_led = request.args.get('state') == 'true'  # Obtiene el estado (true/false)

        if numero_led not in [1, 2, 3]:  # Verifica si el número del LED es válido
            return 'El número de LED debe ser 1, 2 o 3', 400  # Error si es inválido

        # Selecciona el LED correspondiente según el número recibido
        leds = [led_rojo, led_verde, led_azul]
        led_seleccionado = leds[numero_led - 1]

        # Cambia el estado del LED (encendido o apagado)
        led_seleccionado.value(1 if estado_led else 0)

        return f'LED {numero_led} {"encendido" if estado_led else "apagado"}'  # Devuelve confirmación

    except (ValueError, IndexError):  # Controla errores de conversión o índices fuera de rango
        return 'Entrada no válida', 400  # Devuelve error si los datos son incorrectos

# Ruta para controlar el color de la tira NeoPixel
@web_app.route('/color')
def control_color(request):
    try:
        rojo = int(request.args.get('r', 0))  # Obtiene el valor de rojo desde la URL
        verde = int(request.args.get('g', 0))  # Obtiene el valor de verde
        azul = int(request.args.get('b', 0))  # Obtiene el valor de azul

        # Verifica que los valores RGB estén en el rango válido (0-255)
        if not all(0 <= valor <= 255 for valor in (rojo, verde, azul)):
            return 'Los valores RGB deben estar entre 0 y 255', 400  # Devuelve error si no están en el rango

        # Establece el color de la tira NeoPixel y actualiza los LEDs
        tira_led.fill((rojo, verde, azul))
        tira_led.write()

        return f'Color establecido a R:{rojo}, G:{verde}, B:{azul}'  # Confirma el cambio de color

    except ValueError:  # Controla errores de conversión de valores
        return 'Valores RGB no válidos', 400  # Devuelve error si los valores no son correctos

# Inicia el servidor en el puerto 80
web_app.run(port=80)
