from django.db import models
import uuid

ESTADOS = (
    ('SOLICITADO', 'Solicitado'),
    ('APROBADO', 'Aprobado'),
    ('EN_PROCESO', 'En Proceso'),
    ('REALIZADA', 'Realizada'),
    ('ENTREGADA', 'Entregada'),
    ('FINALIZADA', 'Finalizada'),
    ('CANCELADA', 'Cancelada'),
)

PAGOS = (
    ('PENDIENTE', 'Pendiente'),
    ('PARCIAL', 'Parcial'),
    ('PAGADO', 'Pagado'),
)

PLATAFORMAS = (
    ('FACEBOOK', 'Facebook'),
    ('INSTAGRAM', 'Instagram'),
    ('WHATSAPP', 'WhatsApp'),
    ('PRESENCIAL', 'Presencial'),
    ('SITIO_WEB', 'Sitio Web'),
)

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio_base = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos')

class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    marca = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField(blank=True, null=True)
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    red_social_cliente = models.CharField(max_length=100, blank=True, null=True)

    producto_referencia = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True)
    
    descripcion_solicitada = models.TextField()
    fecha_necesidad = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='SOLICITADO')
    estado_pago = models.CharField(max_length=20, choices=PAGOS, default='PENDIENTE')
    plataforma_origen = models.CharField(max_length=20, choices=PLATAFORMAS, default='SITIO_WEB') 

    token_seguimiento = models.UUIDField(default=uuid.uuid4, editable=False) 
    monto_total = models.PositiveIntegerField(default=0)
    monto_abonado = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre_cliente

class ImagenReferencia(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='imagenes_referencia', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='referencias')

class Comentario(models.Model):
    producto = models.ForeignKey(Producto, related_name='comentarios', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre