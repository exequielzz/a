from django.contrib import admin
from django.urls import path, include # Importamos include para incluir otras urls
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views
from rest_framework.routers import DefaultRouter

# Router para ViewSets automáticos
router = DefaultRouter() # Creamos un router por defecto
router.register(r'insumos', views.InsumoViewSet) # API 1
router.register(r'pedidos', views.PedidoCreateUpdateViewSet) # API 2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalogo, name='catalogo'),
    path('producto/<slug:slug>/', views.producto_detalle, name='producto_detalle'),
    path('solicitar/', views.solicitar_pedido, name='solicitar_pedido'),
    path('solicitar/<int:producto_id>/', views.solicitar_pedido, name='solicitar_pedido_producto'),
    path('seguimiento/<uuid:token>/', views.seguimiento, name='seguimiento'),
    path('reporte/', views.reporte_sistema, name='reporte_sistema'), # Nueva ruta para reporte
    path('api/', include(router.urls)), # API 1 y 2
    path('api/pedidos/filtrar/', views.PedidoFilterView.as_view(), name='api_pedidos_filtrar'), # API 3
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)