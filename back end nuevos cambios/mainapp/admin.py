from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import Categoria, Producto, ProductoImagen, Insumo, Pedido, ImagenReferencia, Comentario

class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    max_num = 3
    fields = ('imagen', 'vista_previa',)
    readonly_fields = ('vista_previa',)

    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" />', obj.imagen.url)
        return 'Sin imagen'

class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 0
    max_num = 3
    fields = ('imagen', 'vista_previa',)
    readonly_fields = ('vista_previa',)

    def vista_previa(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="100" />', obj.imagen.url)
        return 'Sin imagen'

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_base', 'destacado', 'ver_imagen')
    list_filter = ('categoria', 'destacado')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ProductoImagenInline]

    def ver_imagen(self, obj):
        img = obj.imagenes.first()
        if img:
            return format_html('<img src="{}" width="50" />', img.imagen.url)
        return '-'

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'cantidad_disponible', 'marca')
    list_filter = ('tipo', 'marca')
    actions = ['aumentar_stock']

    @admin.action(description='Aumentar stock en 10')
    def aumentar_stock(self, request, queryset):
        for insumo in queryset:
            insumo.cantidad_disponible += 10
            insumo.save()
        self.message_user(request, "Stock actualizado correctamente.")

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'estado', 'estado_pago', 'monto_total', 'link_seguimiento')
    list_filter = ('estado', 'estado_pago', 'fecha_creacion')
    search_fields = ('nombre_cliente', 'token_seguimiento')
    inlines = [ImagenReferenciaInline]
    
    readonly_fields = ('token_seguimiento', 'fecha_creacion', 'link_seguimiento')

    fieldsets = (
        ('Cliente', {'fields': ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'red_social_cliente')}),
        ('Pedido', {'fields': ('producto_referencia', 'descripcion_solicitada', 'fecha_necesidad')}),
        ('Estado', {'fields': ('estado', 'estado_pago', 'monto_total', 'monto_abonado')}),
        ('Sistema', {'fields': ('plataforma_origen', 'token_seguimiento', 'link_seguimiento', 'fecha_creacion')}),
    )

    def save_model(self, request, obj, form, change):
        if obj.estado == 'FINALIZADA' and obj.estado_pago != 'PAGADO':
            messages.error(request, 'ERROR: No puedes finalizar el pedido si no está PAGADO.')
            return 
        super().save_model(request, obj, form, change)

    def link_seguimiento(self, obj):
        url = reverse('seguimiento', args=[obj.token_seguimiento])
        full_url = f"http://127.0.0.1:8000{url}"
        return format_html('<a href="{}" target="_blank">Ver Seguimiento</a>', full_url)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'producto', 'fecha')
    list_filter = ('fecha',)