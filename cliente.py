import socket
import threading


HOST = "192.168.20.68"   # localhost (mismo PC)
PUERTO = 5000


def escuchar_servidor(cliente_socket, conectado):
    while conectado[0]:
        try:
            datos = cliente_socket.recv(1024)
            if not datos:
                print("\n[!] El servidor cerró la conexión.")
                conectado[0] = False
                break
            print(datos.decode("utf-8"), end="")
        except OSError:
            
            break
        except Exception as e:
            print(f"\n[ERROR al recibir] {e}")
            conectado[0] = False
            break


def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("=" * 45)
    print("  💬 MiniDistributedChat — CLIENTE")
    print(f"  Conectando a {HOST}:{PUERTO} ...")
    print("=" * 45)

    try:
        cliente.connect((HOST, PUERTO))
    except ConnectionRefusedError:
        print("[ERROR] No se pudo conectar. ¿El servidor está encendido?")
        return
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print("✅ Conectado al servidor!\n")
    print("Comandos disponibles:")
    print("  JOIN <tu_nombre>  — Unirte al chat")
    print("  MSG <texto>       — Enviar un mensaje")
    print("  EXIT              — Salir del chat")
    print("-" * 45)

    # Flag compartido entre hilos para saber si seguimos conectados
    conectado = [True]

    # Hilo que escucha mensajes del servidor en segundo plano
    hilo_receptor = threading.Thread(
        target=escuchar_servidor,
        args=(cliente, conectado),
        daemon=True
    )
    hilo_receptor.start()

    # Bucle principal: leer input del usuario y enviar 
    try:
        while conectado[0]:
            try:
                entrada = input()
            except EOFError:
                break

            if not entrada.strip():
                continue

            # Validar formato básico antes de enviar
            upper = entrada.strip().upper()

            if not (upper.startswith("JOIN ") or
                    upper.startswith("MSG ")  or
                    upper == "EXIT"):
                print("[!] Comando inválido. Usa: JOIN <nombre> | MSG <texto> | EXIT")
                continue

            try:
                cliente.send(entrada.strip().encode("utf-8"))
            except Exception:
                print("[!] Error al enviar. Conexión perdida.")
                break

            # Si el usuario escribió EXIT, esperar la respuesta y salir
            if upper == "EXIT":
                import time
                time.sleep(0.3)  # Dar tiempo a que llegue el "Hasta luego"
                conectado[0] = False
                break

    except KeyboardInterrupt:
        print("\n[!] Desconectando...")
        try:
            cliente.send("EXIT".encode("utf-8"))
        except Exception:
            pass

    finally:
        cliente.close()
        print("👋 Desconectado del servidor. ¡Hasta luego!")


if __name__ == "__main__":
    iniciar_cliente()