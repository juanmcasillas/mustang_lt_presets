import time
import ltamp
import json

# 1. Inicializar y conectar con el amplificador por USB
amp = ltamp.LtAmp()
amp.connect()

try:
    # 2. Protocolo de inicialización obligatorio
    amp.send_sync_begin()
    amp.send_sync_end()

    # 3. Elegir el slot del perfil que deseas modificar (ej. Slot 5)
    slot_id = 60
    amp.set_preset(slot_id)
    print(dir(amp))

    # 4. Obtener la estructura de datos del preset actual
    # Esto recupera el objeto protobuf correspondiente al sonido cargado
    # preset_data = amp.request_current_preset()
    preset_data = amp.retrieve_preset(slot_id)
    if preset_data:
        print(preset_data)

        data = json.loads(preset_data["data"])
        print(f"Modificando el perfil actual: {data["info"]["displayName"]}")

        # --- MODIFICACIONES DEL PERFIL ---
        
        # Ejemplo A: Cambiar el nombre del preset
        data["info"]["displayName"] = "TESTING"

        # Ejemplo B: Modificar ecualización o ganancia (nombres de variable basados en el protobuf de la librería)
        # Nota: Los rangos y nombres exactos mapean los potenciómetros virtuales del ampli (ej. Gain, Bass, Middle, Treble)
        # if hasattr(preset_data, 'gain'):
        #     preset_data.gain = 75  # Ajusta la ganancia (valor numérico de 0 a 100 generalmente)
        # if hasattr(preset_data, 'bass'):
        #     preset_data.bass = 60  # Modifica los graves
            
        # 5. Grabar los cambios en la memoria del amplificador
        # Se envía el objeto modificado de vuelta indicando el slot objetivo
        amp.save_preset_as(json.dumps(data), True, slot_id) # for now, the same data read to test
        print(f"¡Cambios guardados permanentemente en el slot {slot_id}!")
    else:
        print("No se pudo leer la información del perfil del amplificador.")

    # 6. Mantener la señal de latido (heartbeat) por seguridad antes de salir
    for i in range(3):
        amp.send_heartbeat()
        time.sleep(1)

finally:
    # 7. Desconexión limpia del bus USB
    amp.disconnect()
    print("Conexión finalizada.")
