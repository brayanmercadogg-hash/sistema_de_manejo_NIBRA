import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

FILE_PRODUCTOS = 'productos.json'
FILE_HISTORIAL = 'historial.json'

def cargar_json(archivo):
    if not os.path.exists(archivo): return []
    with open(archivo, 'r') as f: return json.load(f)

def guardar_json(archivo, datos):
    with open(archivo, 'w') as f: json.dump(datos, f, indent=4)

def registrar_historial(accion, detalle):
    historial = cargar_json(FILE_HISTORIAL)
    historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accion": accion,
        "detalle": detalle
    })
    guardar_json(FILE_HISTORIAL, historial)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ejecutar', methods=['POST'])
def ejecutar():
    comando = request.get_json().get('comando', '').strip().split()
    if not comando: return jsonify({'respuesta': ''})

    cmd, args = comando[0].lower(), comando[1:]
    productos = cargar_json(FILE_PRODUCTOS)

    if cmd == 'help':
        resp = "Comandos:\n- add [nombre] [precio] : Agrega un producto\n- del [id] : Elimina un producto\n- list : Muestra productos\n- history : Muestra historial de cambios"
    
    elif cmd == 'add':
        if len(args) < 2: return jsonify({'respuesta': "Uso: add [nombre] [precio]"})
        precio = args[-1]
        nombre = " ".join(args[:-1])
        nuevo_id = 1 if not productos else productos[-1]['id'] + 1
        productos.append({"id": nuevo_id, "nombre": nombre, "precio": precio})
        guardar_json(FILE_PRODUCTOS, productos)
        registrar_historial("AGREGAR", f"[{nuevo_id}] {nombre} - ${precio}")
        resp = f"OK. Producto {nuevo_id} agregado."

    elif cmd == 'del':
        if not args: return jsonify({'respuesta': "Uso: del [id]"})
        id_borrar = int(args[0])
        prod = next((p for p in productos if p['id'] == id_borrar), None)
        if prod:
            productos = [p for p in productos if p['id'] != id_borrar]
            guardar_json(FILE_PRODUCTOS, productos)
            registrar_historial("ELIMINAR", f"[{id_borrar}] {prod['nombre']}")
            resp = f"OK. Producto {id_borrar} eliminado."
        else:
            resp = "Error: ID no encontrado."

    elif cmd == 'list':
        if not productos: resp = "Sin productos."
        else: resp = "ID | Nombre | Precio\n" + "\n".join([f"{p['id']} | {p['nombre']} | ${p['precio']}" for p in productos])

    elif cmd == 'history':
        hist = cargar_json(FILE_HISTORIAL)
        resp = "HISTORIAL:\n" + "\n".join([f"[{h['fecha']}] {h['accion']}: {h['detalle']}" for h in hist])

    else:
        resp = f"Comando no reconocido."

    return jsonify({'respuesta': resp})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
