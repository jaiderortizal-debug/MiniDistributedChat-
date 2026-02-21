import socket
import threading


HOST = "0.0.0.0"   
PUERTO = 5000


clientes = {}        # { socket: nombre }
lock = threading.Lock()  


def broadcast(mensaje, origen_socket=None):
    with lock:
        for cliente_socket in list(clientes.keys()):
            if cliente_socket != origen_socket:
                try:
                    cliente_socket.send(mensaje.encode("utf-8"))
                except Exception:
                    # Si falla el envío, ignorar (ya se manejará en su hilo)
                    pass


def manejar_cliente(cliente_socket, direccion):
    print(f"[+] Nueva conexión desde {direccion}")
    nombre = None

    try:
        while True:
            # Recibir mensaje del cliente (hasta 1024 bytes)
            datos = cliente_socket.recv(1024)

            # Si recv devuelve vacío, el cliente cerró la conexión
            if not datos:
                break

            mensaje = datos.decode("utf-8").strip()
            print(f"[DEBUG] Recibido de {direccion}: {mensaje}")

            #Protocolo de comandos ─
            if mensaje.startswith("JOIN "):
                # JOIN <nombre>
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
                    broadcast(f"[SERVIDOR] {nombre} se ha unido al chat.\n", cliente_socket)
                    print(f"[+] {nombre} se unió desde {direccion}")

            elif mensaje.startswith("MSG "):
                # MSG <texto>
                if nombre is None:
                    cliente_socket.send("ERROR Debes hacer JOIN primero.\n".encode("utf-8"))
                else:
                    texto = mensaje[4:].strip()
                    if texto:
                        broadcast(f"[{nombre}]: {texto}\n", cliente_socket)
                        cliente_socket.send(f"[Tú]: {texto}\n".encode("utf-8"))

            elif mensaje == "EXIT":
                # EXIT — el cliente se despide correctamente
                cliente_socket.send("OK Hasta luego!\n".encode("utf-8"))
                break

            else:
                cliente_socket.send("ERROR Comando desconocido. Usa: JOIN <nombre> | MSG <texto> | EXIT\n".encode("utf-8"))

    except ConnectionResetError:
        print(f"[-] Conexión interrumpida desde {direccion}")
    except Exception as e:
        print(f"[ERROR] {direccion}: {e}")
    finally:
        #  Limpieza: eliminar cliente de la lista ─
        with lock:
            if cliente_socket in clientes:
                del clientes[cliente_socket]
        cliente_socket.close()

        if nombre:
            broadcast(f"[SERVIDOR] {nombre} ha abandonado el chat.\n")
            print(f"[-] {nombre} desconectado de {direccion}")
        else:
            print(f"[-] Cliente anónimo desconectado de {direccion}")


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reusar el puerto si el servidor se reinicia rápido
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PUERTO))
    servidor.listen()

    print("=" * 45)
    print("  ✅ MiniDistributedChat — SERVIDOR")
    print(f"  Escuchando en {HOST}:{PUERTO}")
    print("  Esperando clientes... (Ctrl+C para salir)")
    print("=" * 45)

    try:
        while True:
            # accept() bloquea hasta que llega un cliente
            cliente_socket, direccion = servidor.accept()

        
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(cliente_socket, direccion),
                daemon=True  # El hilo muere si el servidor cierra
            )
            hilo.start()

            with lock:
                total = len(clientes)
            print(f"[INFO] Clientes conectados actualmente: {total}")

    except KeyboardInterrupt:
        print("\n[!] Servidor apagado por el administrador.")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor()