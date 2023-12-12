from flask import Flask, jsonify, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database import engine,crear_nuevo_pedido,obtener_detalles_pedidos, obtener_todos_los_pedidos, obtener_pedidos_de_cliente, borrar_pedido, actualizar_pedido, crear_nuevo_cliente, obtener_todos_los_clientes, obtener_cliente_por_id, actualizar_cliente, borrar_cliente, crear_nuevo_detalles, obtener_ultimo_pedido_id, obtener_todos_los_detalles, actualizar_detalles, borrar_detalle


app = Flask(__name__)
port_number = 5000

# Configure rate limiting for API endpoints
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

#    Generate a JSON error response with the given message and status code.
def generate_error_response(message, status_code):
    return jsonify({"message": message}), status_code

@limiter.limit("5 per minute")
@app.route('/')
def home():
    return render_template('index.html')

@limiter.limit("10 per minute")
@app.route('/lped', methods = ['POST'])
def crear_nuevo_pedido_route():
    data = request.json
    if data is None:
        return generate_error_response("Datos JSON no válidos", 400)

    required_fields = ['clientesid', 'viaid', 'almacenid']

    for field in required_fields:
        if field not in data or not data[field]:
            return generate_error_response(f"Campo requerido no proporcionado: {field}", 400)

    clientesid = data.get('clientesid')
    viaid = data.get('viaid')
    almacenid = data.get('almacenid')

    nuevo_pedido = crear_nuevo_pedido(clientesid, viaid, almacenid)

    if nuevo_pedido:
        return jsonify({"message": "Nuevo pedido creado", "pedido": nuevo_pedido}), 201
    else:
        return generate_error_response("Error al crear el pedido", 500)

@limiter.limit("10 per minute")
@app.route('/opedidos', methods=['GET'])
def obtener_todos_los_pedidos_route():
    pedidos = obtener_todos_los_pedidos()
    return jsonify(pedidos)

@app.route('/opedidos/<cliente_id>', methods=['GET'])
def obtener_pedidos_cliente_route(cliente_id):
    pedidos_cliente = obtener_pedidos_de_cliente(cliente_id)

    if pedidos_cliente:
        return jsonify({"pedidos": pedidos_cliente}), 200
    else:
        return generate_error_response(f"No se encontraron pedidos para el ClienteID: {cliente_id}", 404)

@app.route('/pedido/<int:pedido_id>', methods=['PUT'])
def actualizar_pedido_route(pedido_id):
    udata = request.json
    if udata is None:
        return generate_error_response("Datos JSON no válidos", 400)

    nuevos_valores = udata.get('nuevos_valores')

    if actualizar_pedido(pedido_id, nuevos_valores):
        return jsonify({"message": f"Pedido {pedido_id} actualizado exitosamente"}), 200
    else:
        return generate_error_response(f"No se encontró el pedido {pedido_id} o no se realizaron cambios", 404)

@app.route('/bpedido/<int:listapedidoID>', methods=['DELETE'])
def borrar_pedidos_route(listapedidoID):
    resultado_borrar_pedido = borrar_pedido(listapedidoID)

    if resultado_borrar_pedido and resultado_borrar_pedido[0]:
        return jsonify({"success": True, "message": "Lista de Pedidos eliminado"}), resultado_borrar_pedido[1]
    else:
        return generate_error_response("Error al eliminar la lista de pedidos", 500)
    
@limiter.limit("10 per minute")
@app.route('/cliente', methods = ['POST'])
def crear_nuevo_cliente_route():
    data = request.json
    if data is None:
        return generate_error_response("Datos JSON no válidos", 400)

    required_fields = ['nombres', 'apellidos', 'direccion', 'cedula', 'telefono', 'tipopago']

    for field in required_fields:
        if field not in data or not data[field]:
            return generate_error_response(f"Campo requerido no proporcionado: {field}", 400)

    nombres = data.get('nombres')
    apellidos = data.get('apellidos')
    direccion = data.get('direccion')
    cedula = data.get('cedula')
    telefono = data.get('telefono')
    tipopago = data.get('tipopago')

    nuevo_cliente = crear_nuevo_cliente(nombres, apellidos, direccion, cedula, telefono, tipopago)

    if nuevo_cliente:
        return jsonify({"message": "Nuevo cliente creado", "cliente": nuevo_cliente}), 201
    else:
        return generate_error_response("Error al crear el cliente", 500)

@limiter.limit("10 per minute")
@app.route('/ocliente', methods=['GET'])
def obtener_todos_los_clientes_route():
    clientes = obtener_todos_los_clientes()
    return jsonify(clientes)

@app.route('/ocliente/<cliente_id>', methods=['GET'])
def obtener_id_cliente_route(cliente_id):
    cliente = obtener_cliente_por_id(cliente_id)

    if cliente:
        return jsonify({"cliente": cliente}), 200
    else:
        return generate_error_response(f"No se encontró el cliente con ID: {cliente_id}", 404)

@app.route('/cliente/<int:cliente_id>', methods=['PUT'])
def actualizar_cliente_route(cliente_id):
    data = request.json
    if data is None:
        return generate_error_response("Datos JSON no válidos", 400)

    nuevos_valores = data.get('nuevos_valores')

    if actualizar_cliente(cliente_id, nuevos_valores):
        return jsonify({"message": f"Cliente {cliente_id} actualizado exitosamente"}), 200
    else:
        return generate_error_response(f"No se encontró el cliente {cliente_id} o no se realizaron cambios", 404)

@app.route('/bcliente/<int:cliente_id>', methods=['DELETE'])
def borrar_cliente_route(cliente_id):
    resultado_borrar_cliente = borrar_cliente(cliente_id)

    if resultado_borrar_cliente and resultado_borrar_cliente[0]:
        return jsonify({"success": True, "message": "Cliente eliminado"}), resultado_borrar_cliente[1]
    else:
        return generate_error_response("Error al eliminar el cliente", 500)
 
@limiter.limit("10 per minute")
@app.route('/detalles', methods=['POST'])
def crear_nuevo_detalles_route():
    data = request.json
    if data is None:
        return generate_error_response("Datos JSON no válidos", 400)

    ultimo_pedido_id = obtener_ultimo_pedido_id()

    if ultimo_pedido_id is not None:
        ProductoID = data.get('ProductoID')
        AlmacenID = data.get('AlmacenID')
        Cantidad = data.get('Cantidad')
        Costo = data.get('Costo')

        nuevo_detalles = crear_nuevo_detalles(ultimo_pedido_id, ProductoID, AlmacenID, Cantidad, Costo)

        if nuevo_detalles:
            return jsonify({"message": "Detalles del producto creados exitosamente", "detalles": nuevo_detalles}), 201
        else:
            return generate_error_response("Error al crear detalles del producto", 500)
    else:
        return generate_error_response("No hay listas de pedidos disponibles", 404)

@limiter.limit("10 per minute")
@app.route('/odetalles', methods=['GET'])
def obtener_todos_los_detalles_route():
    detalles = obtener_todos_los_detalles()
    return jsonify(detalles)

@app.route('/detalle/<int:DetalleID>', methods=['PUT'])
def actualizar_detalles_route(DetalleID):
    data = request.json
    if data is None:
        return generate_error_response("Datos JSON no válidos", 400)

    nuevos_valores = data.get('nuevos_valores')

    if actualizar_detalles(DetalleID, nuevos_valores):
        return jsonify({"message": f"Los detalles del producto {DetalleID} actualizado exitosamente"}), 200
    else:
        return generate_error_response(f"No se encontró el detalle del producto {DetalleID} o no se realizaron cambios", 404)

@app.route('/bdetalles/<int:DetalleID>', methods=['DELETE'])
def borrar_detalles_route(DetalleID):
    resultado_borrar_detalle = borrar_detalle(DetalleID)

    if resultado_borrar_detalle and resultado_borrar_detalle[0]:
        return jsonify({"success": True, "message": "Detalles del producto eliminados"}), resultado_borrar_detalle[1]
    else:
        return generate_error_response("Error al eliminar los detalles del producto", 500)

@app.route('/detalles_pedidos', methods=['GET'])
def obtener_detalles_pedidos_route():
    detalles_pedidos = obtener_detalles_pedidos()
    return jsonify(detalles_pedidos)

if __name__ == '__main__':
    app.run(host='localhost', port=port_number)