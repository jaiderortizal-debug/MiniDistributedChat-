import socket
import threading
import time

HOST = "10.43.127.195"
PUERTO = 5000


def manejar_respuesta(respuesta):
    """Interpreta el codigo de estado de la respuesta del servidor."""
    codigo = respuesta[:3]
    cuerpo = respuesta[4:].strip() if len(respuesta) > 4 else ""

    if codigo == "200":
        print(f"[200 OK] {cuerpo}")
    elif codigo == "401":
        print(f"[401 UNAUTHORIZED] {cuerpo}")
    elif codigo == "403":
        print(f"[403 FORBIDDEN] {cuerpo}")
    elif codigo == "409":
        print(f"[409 CONFLICT] {cuerpo}")
    elif codigo == "400":
        print(f"[400 BAD REQUEST] {cuerpo}")
    elif codigo == "500":
        print(f"[500 ERROR] {cuerpo}")
    else:
        # Mensajes de broadcast (no tienen codigo, ej: "[Juan]: hola")
        print(respuesta, end="")


def escuchar_servidor(conn, conectado):
    while conectado[0]:
        try:
            datos = conn.recv(1024)
            if not datos:
                print("\nEl servidor cerro la conexion.")
                conectado[0] = False
                break
            for linea in datos.decode("utf-8").splitlines():
                if linea.strip():
                    manejar_respuesta(linea)
        except OSError:
            break
        except Exception as e:
            print(f"\nError al recibir: {e}")
            conectado[0] = False
            break


def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Conectando a {HOST}:{PUERTO}...")

    try:
        cliente.connect((HOST, PUERTO))
    except ConnectionRefusedError:
        print("No se pudo conectar. El servidor esta apagado?")
        return
    except Exception as e:
        print(f"Error: {e}")
        return

    print("Conectado al servidor.")
    print("Comandos: LOGIN <nombre> | MSG <texto> | EXIT")
    print("Codigos de respuesta: 200 OK | 400 | 401 | 403 | 409 | 500\n")

    conectado = [True]
    threading.Thread(target=escuchar_servidor, args=(cliente, conectado), daemon=True).start()

    try:
        while conectado[0]:
            try:
                entrada = input().strip()
            except EOFError:
                break

            if not entrada:
                continue

            upper = entrada.upper()
            if not (upper.startswith("LOGIN ") or upper.startswith("MSG ") or upper == "EXIT"):
                print("Comando invalido. Usa: LOGIN <nombre> | MSG <texto> | EXIT")
                continue

            try:
                cliente.send(entrada.encode("utf-8"))
            except Exception:
                print("Error al enviar. Conexion perdida.")
                break

            if upper == "EXIT":
                time.sleep(0.3)
                conectado[0] = False
                break

    except KeyboardInterrupt:
        print("\nDesconectando...")
        try:
            cliente.send("EXIT".encode("utf-8"))
        except Exception:
            pass
    finally:
        cliente.close()
        print("Desconectado.")


if __name__ == "__main__":
    iniciar_cliente()
