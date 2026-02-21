# Chat en tiempo real con servidor concurrente y múltiples clientes.

---

# 1. Descargar el proyecto

## Opción A – Desde GitHub (si sabes usar git)

```bash
git clone https://github.com/jaiderortizal-debug/MiniDistributedChat-.git
cd MiniDistributedChat
```

## Opción B – Descargar manualmente

1. Descargar el archivo `.zip`
2. Extraerlo
3. Abrir la carpeta del proyecto

---

# 2. Requisitos

* Python 3.8 o superior
  Verifica con:

```bash
python --version
```

Si no lo tienes, descárgalo desde:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

* Dos o más computadores conectados a la **misma red WiFi o LAN**

---

# 3. Cómo saber la IP del servidor?

La IP es necesaria para que los clientes puedan conectarse.

## En Windows:

1. Presiona `Win + R`
2. Escribe `cmd`
3. Ejecuta:

```bash
ipconfig
```

Busca algo como:

```
Dirección IPv4. . . . . . . . . . . : 192.168.1.50
```

Esa es tu IP.

---

## En Linux o Mac:

```bash
ifconfig
```

o

```bash
ip a
```

Busca algo como:

```
inet 192.168.1.50
```

---

# 4. Ejecutar el servidor

En la computadora que será el servidor:

```bash
python server.py
```

Verás algo como:

```
Servidor escuchando en 0.0.0.0:5000
```

Eso significa que está listo.

> [!WARNING]
> No cierres esta ventana.

---

# 5. Ejecutar el cliente

En la computadora cliente:

1. Abre `client.py`
2. Cambia esta línea:

```python
HOST = "192.168.20.68"
```

[Por la IP real del servidor que te arrojo la terminal en el paso 3](#3-como-saber-la-ip-del-servidor)

3. Guarda el archivo
4. Ejecuta:

```bash
python client.py
```

---

# 6. Protocolo de comandos

| Comando         | Descripción         |
| --------------- | ------------------- |
| `JOIN <nombre>` | Unirse al chat      |
| `MSG <texto>`   | Enviar mensaje      |
| `EXIT`          | Salir correctamente |

Ejemplo:

```
JOIN Ana
MSG Hola a todos
EXIT
```