import sqlalchemy
from sqlalchemy import create_engine, outerjoin,Table, Column, Integer, String, MetaData, DECIMAL, text, select, func, desc, DateTime
from datetime import datetime
from sqlalchemy.sql import select, and_
import pprint
from sqlalchemy.orm import aliased


connection_string = 'mysql+pymysql://root:jotita@127.0.0.1:3306/redinventario?autocommit=true'
engine = create_engine(connection_string, echo=True)
conn = engine.connect()

metadata = MetaData()

# Define your tables
Clientes = Table('Clientes', metadata, autoload_with=engine)
ListaPedidos = Table('ListaPedidos', metadata, autoload_with=engine)
Almacen = Table('Almacen', metadata, autoload_with=engine)
TarifasTransporte = Table('TarifasTransporte', metadata, autoload_with=engine)
ViasEmbarque = Table('ViasEmbarque', metadata, autoload_with=engine)
Producto = Table('Producto', metadata, autoload_with=engine)
Detalles = Table('DetallesPedido', metadata, autoload_with=engine)


#Clientes OPERACIONES--------------------------------------------------------------------------------------------------------------
def crear_nuevo_cliente(nombres, apellidos, direccion, cedula, telefono, tipo_pago):
    nuevo_cliente = Clientes.insert().values(
        Nombres=nombres,
        Apellidos=apellidos,
        Direccion=direccion,
        Cedula=cedula,
        Telefono=telefono,
        TipoPago=tipo_pago
    )

    # Ejecutar la instrucción de inserción
    result = conn.execute(nuevo_cliente)
    nuevo_cliente_id = result.lastrowid

    if nuevo_cliente_id:
        # Recuperar la información del nuevo cliente
        nuevo_cliente_info = conn.execute(select(Clientes).filter(Clientes.c.ClientesID == nuevo_cliente_id)).fetchone()

        # Verificar si se recuperó la información del cliente antes de crear el diccionario
        if nuevo_cliente_info:
            print("Informacion del nuevo cliente:", nuevo_cliente_info)
            return dict(zip(Clientes.columns.keys(), nuevo_cliente_info))

    print("No se pudo obtener la informacion del nuevo cliente.")
    return None  # Devolver None si no se creó un nuevo cliente

def obtener_todos_los_clientes():
    result_clientes = conn.execute(select(Clientes)).fetchall()
    # Obtener los nombres de las columnas de la tabla Clientes
    column_names = Clientes.columns.keys()
    # Crear una lista de diccionarios con los resultados
    clientes_list = [dict(zip(column_names, result)) for result in result_clientes]
    return clientes_list

    
def obtener_cliente_por_id(cliente_id):
    result_cliente = conn.execute(select(Clientes).where(Clientes.c.ClientesID == cliente_id)).fetchone()
    # Verificar si se encontró el cliente
    if result_cliente:
        # Obtener los nombres de las columnas de la tabla Clientes
        column_names = Clientes.columns.keys()
        # Crear un diccionario con los resultados
        cliente_dict = dict(zip(column_names, result_cliente))
        return cliente_dict
    else:
        return None 
    
def actualizar_cliente(cliente_id, nuevos_valores):
    try:
        stmt = Clientes.update().where(Clientes.c.ClientesID == cliente_id).values(nuevos_valores)
        conn.execute(stmt)
        print(f"Cliente {cliente_id} actualizado con nuevos valores: {nuevos_valores}")
        return True
    except Exception as e:
        print(f"Error al actualizar el cliente {cliente_id}: {e}")
        return False
    
def borrar_cliente(cliente_id):
    result = conn.execute(Clientes.delete().where(Clientes.c.ClientesID == cliente_id))
    
    if result.rowcount > 0:
        print("Cliente eliminado correctamente")
        return True, 200
    else:
        print("Error al intentar eliminar el cliente")
        return False, 500


#borrar_cliente(cliente_id=4)
#actualizar_cliente(cliente_id=1, Telefono="+987654321", Direccion="Nueva dirección")
#obtener_cliente_por_id(cliente_id=18)    
#obtener_todos_los_clientes()
#crear_nuevo_cliente("Juan", "Diaz", "Calle b, Ciudad", "1234567890", "+123456789", 1)

#producto OPERACIONES-------------------------------------------------------------------------------------------------------------

def crear_nuevo_producto(almacen_id, cantidad, peso):
    # Verificar que el AlmacenID existe antes de la inserción
    almacen_existente = conn.execute(select(Almacen).filter(Almacen.c.AlmacenID == almacen_id)).fetchone()
    
    if almacen_existente:
        # Si el AlmacenID existe, realizar la inserción del nuevo producto
        nuevo_producto = Producto.insert().values(
            AlmacenID=almacen_id,
            Cantidad=cantidad,
            Peso=peso
        )
        conn.execute(nuevo_producto)
        print("Nuevo producto creado")
    else:
        print(f"El AlmacenID {almacen_id} no existe. No se puede crear el producto.")

def obtener_todos_los_productos():
    result_productos = conn.execute(select(Producto)).fetchall()
    pprint.pprint(result_productos)

def borrar_producto(producto_id):
    stmt = Producto.delete().where(Producto.c.ProductoID == producto_id)
    result = conn.execute(stmt)
    if result.rowcount > 0:
        print("Producto eliminado")
    else:
        print("No se encontro el producto para eliminar")

def obtener_producto_por_id(producto_id):
    result_producto = conn.execute(select(Producto).filter(Producto.c.ProductoID == producto_id)).fetchone()
    if result_producto:
        pprint.pprint(result_producto)
    else:
        print(f"No se encontro un producto con ProductoID: {producto_id}")

    
def actualizar_producto(producto_id, almacen_id, cantidad=None, peso=None):
    # Verificar que el AlmacenID existe antes de la actualización
    almacen_existente = conn.execute(select(Almacen).filter(Almacen.c.AlmacenID == almacen_id)).fetchone()

    if almacen_existente:
        # Si el AlmacenID existe, realizar la actualización del producto
        update_values = {}
        if cantidad is not None:
            update_values[Producto.c.Cantidad] = cantidad
        if peso is not None:
            update_values[Producto.c.Peso] = peso

        conn.execute(Producto.update().where(and_(Producto.c.ProductoID == producto_id, Producto.c.AlmacenID == almacen_id)).values(update_values))
        print("Producto actualizado")
    else:
        print(f"El AlmacenID {almacen_id} no existe. No se puede actualizar el producto.")


#crear_nuevo_producto( almacen_id=10, cantidad=80, peso=20.5)
#actualizar_producto(producto_id=4, almacen_id=4, cantidad=20, peso=3.0)
#obtener_todos_los_productos()
#borrar_producto(producto_id=7)
#obtener_producto_por_id(producto_id = 10)



#almacen OPERACIONES---------------------------------------------------------------------------------------------------------------

def crear_nuevo_almacen(nombre_almacen, direccion, capacidad, costo_por_unidad, ordenes_por_dia):
    nuevo_almacen = Almacen.insert().values(
        NombreAlmacen=nombre_almacen,
        Direccion=direccion,
        Capacidad=capacidad,
        CostoPorUnidad=costo_por_unidad,
        OrdenesPorDia=ordenes_por_dia
    )
    conn.execute(nuevo_almacen)
    print("Nuevo almacén creado")

def obtener_todos_los_almacenes():
    result_almacenes = conn.execute(select(Almacen)).fetchall()
    pprint.pprint(result_almacenes)

def actualizar_informacion_almacen(almacen_id, nueva_direccion, nuevo_costo_por_unidad):
    stmt = Almacen.update().where(Almacen.c.AlmacenID == almacen_id).values(
        Direccion=nueva_direccion,
        CostoPorUnidad=nuevo_costo_por_unidad
    )
    conn.execute(stmt)
    print("Información de almacén actualizada")

def eliminar_almacen(almacen_id):
    conn.execute(Almacen.delete().where(Almacen.c.AlmacenID == almacen_id))
    print("Almacén eliminado")

#eliminar_almacen(almacen_id=1)
#actualizar_informacion_almacen(almacen_id=1, nueva_direccion="Calle Nueva 456", nuevo_costo_por_unidad=15.0)
#obtener_todos_los_almacenes()
"""crear_nuevo_almacen(
    nombre_almacen="Almacen Principal",
    direccion="Calle Principal 123",
    capacidad=1000,
    costo_por_unidad=10.0,
    ordenes_por_dia=200
)"""


#tarifastransporte OPERACIONES---------------------------------------------------------------------------------------------------

def crear_nueva_tarifa( nombre_courrier, nivel_servicio, costo_tarifa, capacidad):
    nueva_tarifa = TarifasTransporte.insert().values(
        NombreCourrier=nombre_courrier,
        NivelServicio=nivel_servicio,
        CostoTarifa=costo_tarifa,
        Capacidad=capacidad
    )
    conn.execute(nueva_tarifa)
    print("Nueva tarifa de transporte creada")

def obtener_todas_las_tarifas():
    result_tarifas = conn.execute(select(TarifasTransporte)).fetchall()
    pprint.pprint(result_tarifas)

def obtener_tarifa_por_id(courrier_id):
    result_tarifa = conn.execute(select(TarifasTransporte).filter(TarifasTransporte.c.CourrierID == courrier_id)).fetchone()
    pprint.pprint(result_tarifa)

def actualizar_tarifa(courrier_id, nombre_courrier=None, nivel_servicio=None, costo_tarifa=None, capacidad=None):
    # Crear un diccionario con las columnas y sus nuevos valores
    update_values = {}
    if nombre_courrier is not None:
        update_values[TarifasTransporte.c.NombreCourrier] = nombre_courrier
    if nivel_servicio is not None:
        update_values[TarifasTransporte.c.NivelServicio] = nivel_servicio
    if costo_tarifa is not None:
        update_values[TarifasTransporte.c.CostoTarifa] = costo_tarifa
    if capacidad is not None:
        update_values[TarifasTransporte.c.Capacidad] = capacidad

    # Realizar la actualización
    conn.execute(TarifasTransporte.update().where(TarifasTransporte.c.CourrierID == courrier_id).values(update_values))
    print("Tarifa de transporte actualizada")

def borrar_tarifa(courrier_id):
    conn.execute(TarifasTransporte.delete().where(TarifasTransporte.c.CourrierID == courrier_id))
    print("Tarifa de transporte eliminada")

# Ejemplos de uso
#crear_nueva_tarifa( nombre_courrier='Courier1', nivel_servicio='Express', costo_tarifa=50.0, capacidad=100)
#obtener_todas_las_tarifas()
#obtener_tarifa_por_id(courrier_id=1)
#actualizar_tarifa(courrier_id=1, costo_tarifa=60.0)
# borrar_tarifa(courrier_id=1)"""

#ViasEmbarque OPERACIONES--------------------------------------------------------------------------------------------------------


def crear_nueva_via_embarque(courrier_id, puerto_origen, puerto_destino, modo_transporte, distancia):
    # Verificar si existe el courrierID
    if not conn.execute(select(TarifasTransporte.c.CourrierID).where(TarifasTransporte.c.CourrierID == courrier_id)).scalar():
        print(f"Error: No existe el Courrier con ID {courrier_id}")
        return

    # Crear una nueva fila en la tabla ViasEmbarque
    nueva_via_embarque = ViasEmbarque.insert().values(
        CourrierID=courrier_id,
        PuertoOrigen=puerto_origen,
        PuertoDestino=puerto_destino,
        ModoTransporte=modo_transporte,
        Distancia=distancia
    )
    conn.execute(nueva_via_embarque)
    print("Nueva vía de embarque creada")



def obtener_todas_las_vias_embarque():
    result_vias_embarque = conn.execute(select(ViasEmbarque)).fetchall()
    pprint.pprint(result_vias_embarque)


def obtener_vias_por_courier(courrier_id):
    result_vias_courier = conn.execute(select(ViasEmbarque).filter(ViasEmbarque.c.CourrierID == courrier_id)).fetchall()
    pprint.pprint(result_vias_courier)


def actualizar_via_embarque(via_id, courrier_id, nueva_distancia, nuevo_courrier_id=None):
    # Verificar si existe la vía de embarque
    if not conn.execute(select(ViasEmbarque.c.ViaID).where(ViasEmbarque.c.ViaID == via_id)).scalar():
        print(f"Error: No existe la vía de embarque con ID {via_id}")
        return

    # Verificar si existe el CourrierID, si se proporciona
    if nuevo_courrier_id is not None and not conn.execute(select(TarifasTransporte.c.CourrierID).where(TarifasTransporte.c.CourrierID == nuevo_courrier_id)).scalar():
        print(f"Error: No existe el Courrier con ID {nuevo_courrier_id}")
        return

    # Crear un diccionario con las columnas y sus nuevos valores
    update_values = {'Distancia': nueva_distancia}
    if nuevo_courrier_id is not None:
        update_values['CourrierID'] = nuevo_courrier_id

    # Realizar la actualización
    stmt = ViasEmbarque.update().where(ViasEmbarque.c.ViaID == via_id).values(update_values)
    result = conn.execute(stmt)

    # Verificar si se actualizó alguna fila
    if result.rowcount > 0:
        print("Informacion de via de embarque actualizada")
    else:
        print(f"No se encontro la via de embarque con ID {via_id}")


def eliminar_via_embarque(via_id):
    conn.execute(ViasEmbarque.delete().where(ViasEmbarque.c.ViaID == via_id))
    print("Via de embarque eliminada")


#crear_nueva_via_embarque(courrier_id=1, puerto_origen="Puerto A", puerto_destino="Puerto B", modo_transporte="Barco", distancia=500.0)
obtener_todas_las_vias_embarque()
#obtener_vias_por_courier(courrier_id=1)
#actualizar_via_embarque(via_id=1, courrier_id=1, nueva_distancia=800.0)
#eliminar_via_embarque(via_id=3)"""


#lista de pedidos OPERACIONES------------------------------------------------------------------------------------------------------  
def crear_nuevo_pedido(cliente_id, via_id, almacen_id):
    nuevo_pedido = ListaPedidos.insert().values(
        ClientesID=cliente_id,
        ViaID=via_id,
        AlmacenID=almacen_id,
        FechaPedido=datetime.now()
    )
    
    result_pedido = conn.execute(nuevo_pedido)
    nuevo_pedido_id = result_pedido.lastrowid
    print("Nuevo pedido creado")

    if nuevo_pedido_id:
        # Recuperar la información del nuevo cliente
        nuevo_pedido_info = conn.execute(select(ListaPedidos).filter(ListaPedidos.c.listapedidosID == nuevo_pedido_id)).fetchone()

        # Verificar si se recuperó la información del cliente antes de crear el diccionario
        if nuevo_pedido_info:
            print("Informacion del nuevo cliente:", nuevo_pedido_info)
            return dict(zip(ListaPedidos.columns.keys(), nuevo_pedido_info))

    print("No se pudo obtener la informacion del nuevo cliente.")
    return None  # Devolver None si no se creó un nuevo cliente

def obtener_todos_los_pedidos():
    result_pedidos = conn.execute(select(ListaPedidos)).fetchall()
    # Obtener los nombres de las columnas de la tabla Clientes
    column_names = ListaPedidos.columns.keys()
    # Crear una lista de diccionarios con los resultados
    pedidos_list = [dict(zip(column_names, result)) for result in result_pedidos]
    return pedidos_list
    
def obtener_pedidos_de_cliente(cliente_id):
    result_pedidos_id = conn.execute(select(ListaPedidos).filter(ListaPedidos.c.ClientesID == cliente_id)).fetchall()
    # Obtener los nombres de las columnas de la tabla Clientes
    column_names = ListaPedidos.columns.keys()
    # Crear una lista de diccionarios con los resultados
    pedidos_list = [dict(zip(column_names, result)) for result in result_pedidos_id]
    return pedidos_list

def actualizar_pedido(pedido_id, nuevos_valores):
    try:
        stmt = ListaPedidos.update().where(ListaPedidos.c.listapedidosID == pedido_id).values(nuevos_valores)
        conn.execute(stmt)
        print(f"Pedido {pedido_id} actualizado con nuevos valores: {nuevos_valores}")
        return True
    except Exception as e:
        print(f"Error al actualizar pedido {pedido_id}: {e}")
        return False

    
def borrar_pedido(pedido_id):
    result = conn.execute(ListaPedidos.delete().where(ListaPedidos.c.listapedidosID == pedido_id))
    
    if result.rowcount > 0:
        print("Lista de pedido eliminado correctamente")
        return True, 200
    else:
        print("Error al intentar eliminar la lista de pedidos")
        return False, 500
    
#crear_nuevo_pedido(cliente_id=17, via_id=1, almacen_id=1, costo=100.0, lista_productos='Producto1, Producto2')
#obtener_todos_los_pedidos()
#obtener_pedidos_de_cliente(cliente_id=1)

#borrar_pedido(pedido_id=1)

"""listapedidosID = 7
nuevos_valores = {
    "Costo": 150.0,
    "Listaprodutos": "Nuevo Producto",
    "FechaPedido": "2023-12-10"
}
actualizar_pedido(listapedidosID, nuevos_valores)"""

#---------------------------------------------------------------------------
def crear_nuevo_detalles(ListaPedidosID,ProductoID, AlmacenID, Cantidad, Costo):
    nuevo_detalles = Detalles.insert().values(
        ListaPedidosID = ListaPedidosID,
        ProductoID = ProductoID,
        AlmacenID = AlmacenID,
        Cantidad = Cantidad,
        Costo = Costo
    )
    
    result_detalles = conn.execute(nuevo_detalles)
    nuevo_detalles_id = result_detalles.lastrowid
    print("Nuevo detalles del producto creado")

    if nuevo_detalles_id:
        # Recuperar la información del nuevo cliente
        nuevo_detalles_info = conn.execute(select(Detalles).filter(Detalles.c.DetalleID == nuevo_detalles_id)).fetchone()

        # Verificar si se recuperó la información del cliente antes de crear el diccionario
        if nuevo_detalles_info:
            print("Informacion de los detalles del producto:", nuevo_detalles_info)
            return dict(zip(ListaPedidos.columns.keys(), nuevo_detalles_info))

    print("No se pudo obtener la informacion de los detalles del producto.")
    return None  # Devolver None si no se creó un nuevo cliente

#crear_nuevo_detalles(ListaPedidosID=17,ProductoID=6,AlmacenID=2,Cantidad=5,Costo=5.0)

def obtener_ultimo_pedido_id():
    # Obtener el ID de la última lista de pedidos
    ultimo_pedido = conn.execute(ListaPedidos.select().order_by(ListaPedidos.c.listapedidosID.desc()).limit(1)).fetchone()

    if ultimo_pedido:
        return ultimo_pedido.listapedidosID 
    else:
        return None

def obtener_todos_los_detalles():
    result_detalles = conn.execute(select(Detalles)).fetchall()
    # Obtener los nombres de las columnas de la tabla Clientes
    column_names = Detalles.columns.keys()
    # Crear una lista de diccionarios con los resultados
    detalles_list = [dict(zip(column_names, result)) for result in result_detalles]
    return detalles_list

def actualizar_detalles(DetalleID, nuevos_valores):
    try:
        stmt = Detalles.update().where(Detalles.c.DetalleID == DetalleID).values(nuevos_valores)
        conn.execute(stmt)
        print(f"Detalles del producto {DetalleID} actualizado con nuevos valores: {nuevos_valores}")
        return True
    except Exception as e:
        print(f"Error al actualizar los detalles del producto {DetalleID}: {e}")
        return False
    
def borrar_detalle(DetalleID):
    result = conn.execute(Detalles.delete().where(Detalles.c.DetalleID == DetalleID))
    
    if result.rowcount > 0:
        print("Los detalles de producto ha sido eliminado correctamente")
        return True, 200
    else:
        print("Error al intentar eliminar los detalles del producto")
        return False, 500
    
def obtener_detalles_pedidos():
    # Definir la expresión de selección
    query = select(
        ListaPedidos.c.listapedidosID,
        ListaPedidos.c.ClientesID,
        ListaPedidos.c.ViaID,
        ListaPedidos.c.FechaPedido,
        Detalles.c.DetalleID,
        Detalles.c.ProductoID,
        Detalles.c.AlmacenID,
        Detalles.c.Cantidad,
        Detalles.c.Costo
    ).\
    outerjoin(ListaPedidos, ListaPedidos.c.listapedidosID == Detalles.c.ListaPedidosID)
        
    

    detalles_pedidos = conn.execute(query).fetchall()

    column_names = query.columns.keys()
    # Crear una lista de diccionarios con los resultados
    detalles_list = [dict(zip(column_names, result)) for result in detalles_pedidos]
    return detalles_list