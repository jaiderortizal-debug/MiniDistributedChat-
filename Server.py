import socket, threading

# Configuración del servidor
HOST = "0.0.0.0"   # Escucha en todas las interfaces de red disponibles
PUERTO = 5000      # Puerto donde el servidor aceptará conexiones
clientes = {}      # Diccionario que guardará los sockets de los clientes y sus nombres
lock = threading.Lock()  # Candado para evitar conflictos cuando varios hilos acceden a 'clientes'

# Función para enviar un mensaje a todos los clientes conectados (menos el que lo envía, si se indica)
def broadcast(mensaje, origen_socket=None):
    with lock:
        for cliente_socket in list(clientes.keys()):
            if cliente_socket != origen_socket:
                try:
                    cliente_socket.send(mensaje.encode("utf-8"))
                except Exception:
                    # Si hay algún error al enviar (cliente desconectado), simplemente ignorar
                    pass

# Función que maneja la comunicación con un cliente individual
def manejar_cliente(cliente_socket, direccion):
    print(f"[+] Nueva conexión desde {direccion}")
    nombre = None
    try:
        while True:
            datos = cliente_socket.recv(1024)
            if not datos:
                # Si no llega nada, el cliente se desconectó
                break

            mensaje = datos.decode("utf-8").strip()
            print(f"[DEBUG] Recibido de {direccion}: {mensaje}")

            # Si el cliente quiere unirse con un nombre
            if mensaje.upper().startswith("JOIN "):
                nombre_solicitado = mensaje[5:].strip()
                with lock:
                    nombres_activos = list(clientes.values())

                if nombre_solicitado in nombres_activos:
                    cliente_socket.send("ERROR Nombre ya en uso, elige otro.\n".encode("utf-8"))
                elif not nombre_solicitado:
                    cliente_socket.send("ERROR El nombre no puede estar vacío.\n".encode("utf-8"))
                else:
                    nombre = nombre_solicitado
                    with lock:
                        clientes[cliente_socket] = nombre
                    cliente_socket.send(f"OK Bienvenido al chat, {nombre}!\n".encode("utf-8"))
                    broadcast(f"\n[SERVIDOR] {nombre} se ha unido al chat.\n", cliente_socket)
                    print(f"[+] {nombre} se unió desde {direccion}")

            # Si el cliente envía un mensaje
            elif mensaje.upper().startswith("MSG "):
                if nombre is None:
                    cliente_socket.send("ERROR Debes hacer JOIN primero.\n".encode("utf-8"))
                else:
                    texto = mensaje[4:].strip()
                    if texto:
                        broadcast(f"\n[{nombre}]: {texto}\n", cliente_socket)  # A otros clientes
                        cliente_socket.send(f"[Tú]: {texto}\n".encode("utf-8"))  # A sí mismo

            # Si el cliente quiere salir
            elif mensaje.upper() == "EXIT":
                cliente_socket.send("OK Hasta luego!\n".encode("utf-8"))
                break

            # Cualquier otro comando desconocido
            else:
                cliente_socket.send("ERROR Comando desconocido. Usa: JOIN <nombre> | MSG <texto> | EXIT\n".encode("utf-8"))

    except ConnectionResetError:  # Si el cliente se desconecta abruptamente
        print(f"[-] Conexión interrumpida desde {direccion}")
    except Exception as e:
        print(f"[ERROR] {direccion}: {e}")
    finally:
        # Limpiar la conexión
        with lock:
            if cliente_socket in clientes:
                del clientes[cliente_socket]

        cliente_socket.close()
        if nombre:
            broadcast(f"[SERVIDOR] {nombre} ha abandonado el chat.\n")
            print(f"[-] {nombre} desconectado de {direccion}")
        else:
            print(f"[-] Cliente anónimo desconectado de {direccion}")

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crear socket TCP
    servidor.bind((HOST, PUERTO))  # Asocia el socket a la IP y puerto
    servidor.listen()  # Escucha conexiones entrantes
    print(f"Escuchando en {HOST}:{PUERTO}")
    print("Esperando clientes... (Ctrl+C para salir)")
    try:
        while True:  # Bucle principal para aceptar conexiones
            cliente_socket, direccion = servidor.accept()  # Espera a que un cliente se conecte
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(cliente_socket, direccion),
                daemon=True  # El hilo se cerrará automáticamente cuando termine el programa
            )
            hilo.start()  # Inicia el hilo para manejar al cliente

            with lock:
                total = len(clientes)
            print(f"[INFO] Clientes conectados actualmente: {total+1}")
    except KeyboardInterrupt:
        print("\n[!] Servidor apagado por el administrador.")
    finally:
        servidor.close()  # Cerrar el socket al salir

#  Arranca el servidor si se ejecuta directamente este archivo
if __name__ == "__main__":
    main()