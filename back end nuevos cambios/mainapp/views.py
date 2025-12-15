from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto, Categoria, Pedido, ImagenReferencia, Comentario, Insumo
# Aqui importamos las herramientas necesarias de rest framework
from rest_framework import viewsets, mixins, status
# e importamos Response y api_view para manejar las respuestas y vistas de la API
from rest_framework.response import Response
from rest_framework.decorators import APIView
# Importamos Count para agregaciones y login_required para proteger vistas
from django.db.models import Count
from django.contrib.auth.decorators import login_required
# Importamos datetime para manejar fechas
from datetime import datetime
# Importamos los serializers que hemos definido
from .serializers import InsumoSerializer, PedidoSerializer

def catalogo(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    
    
    categoria_seleccionada = request.GET.get('categoria')
    busqueda = request.GET.get('q')

    if categoria_seleccionada:
        productos = productos.filter(categoria__slug=categoria_seleccionada)

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    destacados = Producto.objects.filter(destacado=True)

    context = {
        'productos': productos,
        'categorias': categorias,
        'productos_destacados': destacados
    }
    return render(request, 'catalogo.html', context)

def producto_detalle(request, slug):
    producto = get_object_or_404(Producto, slug=slug)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        texto = request.POST.get('texto')

        if nombre and texto:
            Comentario.objects.create(
                producto=producto,
                nombre=nombre,
                texto=texto
            )
            return redirect('producto_detalle', slug=slug)

    comentarios = producto.comentarios.all().order_by('-fecha')

    return render(request, 'producto_detalle.html', {
        'producto': producto, 
        'comentarios': comentarios
    })

def solicitar_pedido(request, producto_id=None):
    producto_inicial = None
    if producto_id:
        producto_inicial = get_object_or_404(Producto, pk=producto_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_cliente')
        descripcion = request.POST.get('descripcion_solicitada')

        if not nombre or not descripcion:
            messages.error(request, "Faltan datos obligatorios")
            return redirect(request.path)

        producto_final = producto_inicial
        id_referencia = request.POST.get('producto_referencia')
        
        if id_referencia:
            producto_final = Producto.objects.filter(pk=id_referencia).first()

        nuevo_pedido = Pedido.objects.create(
            nombre_cliente=nombre,
            email_cliente=request.POST.get('email_cliente'),
            telefono_cliente=request.POST.get('telefono_cliente'),
            red_social_cliente=request.POST.get('red_social_cliente'),
            descripcion_solicitada=descripcion,
            fecha_necesidad=request.POST.get('fecha_necesidad') or None,
            producto_referencia=producto_final,
            estado='SOLICITADO',
            estado_pago='PENDIENTE',
            plataforma_origen='SITIO_WEB'
        )

        lista_imagenes = request.FILES.getlist('imagenes_referencia')
        
        for imagen in lista_imagenes[:3]:
            ImagenReferencia.objects.create(pedido=nuevo_pedido, imagen=imagen)

        messages.success(request, "Pedido enviado correctamente")
        return redirect('seguimiento', token=nuevo_pedido.token_seguimiento)

    return render(request, 'formulario_solicitud.html', {'producto': producto_inicial})

def seguimiento(request, token):
    pedido = get_object_or_404(Pedido, token_seguimiento=token)
    imagenes = pedido.imagenes_referencia.all()
    
    context = {
        'pedido': pedido,
        'imagenes_referencia': imagenes
    }
    return render(request, 'seguimiento.html', context)

# Vistas de la API para Insumo y Pedido usando viewsets

# --- API 1: CRUD de Insumo ---
class InsumoViewSet(viewsets.ModelViewSet):
    """Permite Crear, Listar, Ver detalle, Modificar y Eliminar Insumos."""
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

# --- API 2: CREAR Y MODIFICAR PEDIDOS (SIN LISTAR NI BORRAR) ---
# Solo permitimos crear y modificar pedidos a traves de las herramientas de rest framework las cuales son: mixins.CreateModelMixin y mixins.UpdateModelMixin
class PedidoCreateUpdateViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    """
    Solo permite Crear (POST) y Modificar (PUT/PATCH).
    No permite Listar (GET list) ni Eliminar (DELETE).
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

# --- API 3: FILTRO DE PEDIDOS ---
class PedidoFilterView(APIView):
    """
    Filtra pedidos por rango de fechas, estado y limita la cantidad.
    URL: /api/pedidos/filtrar/?fecha_inicio=Y-M-D&fecha_fin=Y-M-D&estado=X&limite=N
    """
    def get(self, request):
        # se ocupa get para obtener los parametros de la URL y el request sirve para acceder a ellos
        
        queryset = Pedido.objects.all() #obtenemos todos los pedidos
        fecha_inicio = request.GET.get('fecha_inicio')# obtenemos la fecha de inicio del rango
        fecha_fin = request.GET.get('fecha_fin') # obtenemos la fecha de fin del rango
        
        
        if fecha_inicio and fecha_fin: #si ambas fechas estan presentes
            queryset = queryset.filter(fecha_creacion__date__range=[fecha_inicio, fecha_fin]) #filtramos los pedidos por el rango de fechas

        # Filtro por estado
        estado = request.query_params.get('estado') #obtenemos el estado del pedido
        if estado: #si el estado esta presente
            queryset = queryset.filter(estado=estado) #filtramos los pedidos por el estado

        # Serializar antes de limitar para ordenar si es necesario
        queryset = queryset.order_by('-fecha_creacion') #ordenamos los pedidos por fecha de creacion descendente

        # Limite de resultados
        limite = request.query_params.get('limite') #obtenemos el limite de resultados
        if limite: #si el limite esta presente
            try:
                queryset = queryset[:int(limite)] #limitamos la cantidad de resultados
            except ValueError:
                pass #si el limite no es un entero valido, no hacemos nada

        serializer = PedidoSerializer(queryset, many=True) #serializamos los pedidos
        return Response(serializer.data) #devolvemos la respuesta con los datos serializados
    
# --- VISTA PARA REPORTE DEL SISTEMA ---
@login_required #protege la vista para que solo usuarios autenticados puedan acceder
def reporte_sistema(request): # vista para generar un reporte del sistema
    # Datos para los gráficos
    # 1. Cantidad de pedidos por estado
    pedidos_por_estado = Pedido.objects.values('estado').annotate(total=Count('estado')) # agregamos la cantidad de pedidos por estado
    
    # 2. Pedidos por plataforma
    pedidos_por_plataforma = Pedido.objects.values('plataforma_origen').annotate(total=Count('plataforma_origen')) # agregamos la cantidad de pedidos por plataforma de origen

    # Filtro simple de fechas para la tabla (opcional según requerimiento)
    fecha_inicio = request.GET.get('fecha_inicio') #obtenemos la fecha de inicio del rango
    fecha_fin = request.GET.get('fecha_fin') #obtenemos la fecha de fin del rango
    pedidos_filtrados = Pedido.objects.all() #obtenemos todos los pedidos

    if fecha_inicio and fecha_fin: #si ambas fechas estan presentes
        pedidos_filtrados = pedidos_filtrados.filter(fecha_creacion__date__range=[fecha_inicio, fecha_fin]) #filtramos los pedidos por el rango de fechas

    context = {
        'pedidos_por_estado': list(pedidos_por_estado), # Convertir a lista para usar en JS
        'pedidos_por_plataforma': list(pedidos_por_plataforma), # Convertir a lista para usar en JS
        'pedidos_tabla': pedidos_filtrados, # Pedidos para la tabla
    }
    return render(request, 'reporte.html', context) #renderizamos la plantilla de reporte con el contexto generado