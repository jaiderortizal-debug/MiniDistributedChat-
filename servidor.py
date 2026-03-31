import socket
import threading
import os

HOST = "0.0.0.0"
PUERTO = 5000

clientes = {}
lock = threading.Lock()

def broadcast(mensaje, excluir=None):
    with lock:
        for s in list(clientes.keys()):
            if s != excluir:
                try:
                    s.send(mensaje.encode("utf-8"))
                except Exception:
                    pass


def consola_servidor():
    print("Comandos del servidor: /msg <texto> | /kick <nombre> | /lista | /salir\n")
    while True:
        try:
            entrada = input().strip()
        except EOFError:
            break

        if entrada.startswith("/msg "):
            texto = entrada[5:].strip()
            if texto:
                broadcast(f"[SERVIDOR]: {texto}\n")
                print(f"Enviado a todos: {texto}")

        elif entrada.startswith("/kick "):
            nombre = entrada[6:].strip()
            with lock:
                objetivo = next((s for s, n in clientes.items() if n == nombre), None)
            if objetivo:
                objetivo.send("403 FORBIDDEN Fuiste expulsado por el servidor.\n".encode())
                objetivo.close()
                print(f"{nombre} fue expulsado.")
            else:
                print(f"No existe ningun cliente llamado '{nombre}'.")

        elif entrada == "/lista":
            with lock:
                nombres = list(clientes.values())
            print(f"Conectados ({len(nombres)}): {', '.join(nombres) if nombres else 'ninguno'}")

        elif entrada == "/salir":
            broadcast("[SERVIDOR]: El servidor se esta apagando.\n")
            os._exit(0)

        else:
            print("Comando no reconocido.")


def manejar_cliente(conn, addr):
    nombre = None
    try:
        while True:
            datos = conn.recv(1024)
            if not datos:
                break

            msg = datos.decode("utf-8").strip()
            print(f"[{addr}] >> {msg}")

            # LOGIN <nombre>
            if msg.startswith("LOGIN "):
                n = msg[6:].strip()

                if not n or not n.isalnum():
                    conn.send("401 UNAUTHORIZED Nombre invalido. Solo letras y numeros.\n".encode())

                else:
                    with lock:
                        activos = list(clientes.values())

                    if n in activos:
                        conn.send(f"409 CONFLICT El nombre '{n}' ya esta en uso.\n".encode())
                    else:
                        nombre = n
                        with lock:
                            clientes[conn] = nombre
                        conn.send(f"200 OK Bienvenido, {nombre}!\n".encode())
                        broadcast(f"[SERVIDOR] {nombre} se unio al chat.\n", excluir=conn)
                        print(f"{nombre} autentic desde {addr}")

            # MSG <texto>
            elif msg.startswith("MSG "):
                if not nombre:
                    conn.send("403 FORBIDDEN Debes hacer LOGIN primero.\n".encode())
                else:
                    texto = msg[4:].strip()
                    if texto:
                        broadcast(f"[{nombre}]: {texto}\n", excluir=conn)
                        conn.send(f"200 OK [{nombre}]: {texto}\n".encode())

            # EXIT
            elif msg == "EXIT":
                conn.send("200 OK Hasta luego!\n".encode())
                break

            # Comando desconocido
            else:
                conn.send("400 BAD REQUEST Comandos validos: LOGIN <nombre> | MSG <texto> | EXIT\n".encode())

    except ConnectionResetError:
        pass
    except Exception as e:
        try:
            conn.send(f"500 ERROR Fallo interno: {e}\n".encode())
        except Exception:
            pass
    finally:
        with lock:
            clientes.pop(conn, None)
        conn.close()
        if nombre:
            broadcast(f"[SERVIDOR] {nombre} abandono el chat.\n")
            print(f"{nombre} se desconecto.")


def iniciar():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen()
    print(f"Servidor escuchando en {HOST}:{PUERTO}")
    print("Protocolo activo: LOGIN | MSG | EXIT")
    print("Codigos: 200 OK | 400 BAD REQUEST | 401 UNAUTHORIZED | 403 FORBIDDEN | 409 CONFLICT | 500 ERROR\n")

    threading.Thread(target=consola_servidor, daemon=True).start()

    try:
        while True:
            conn, addr = servidor.accept()
            threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True).start()
            with lock:
                print(f"Nueva conexion desde {addr} | Clientes: {len(clientes)}")
    except KeyboardInterrupt:
        print("Servidor cerrado.")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar()
