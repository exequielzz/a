#los serializers permiten convertir los datos complejos como los queryset y los modelos de Django en tipos de datos nativos de Python que luego pueden ser fácilmente renderizados en JSON, XML u otros formatos de contenido.
from rest_framework import serializers #importamos serializers de rest framework
from .models import Insumo, Pedido  #importamos los modelos que queremos serializar

#aqui definimos el serializer para el modelo Insumo
class InsumoSerializer(serializers.ModelSerializer):
    #clase Meta para definir el modelo y los campos
    class Meta:
        model = Insumo  #especificamos el modelo a serializar
        fields = '__all__'  #especificamos los campos que queremos incluir en la serializacion

#aqui definimos el serializer para el modelo Pedido
class PedidoSerializer(serializers.ModelSerializer):
    #clase Meta para definir el modelo y los campos
    class Meta:
        model = Pedido  #especificamos el modelo a serializar
        fields = '__all__'  #especificamos los campos que queremos incluir en la serializacion