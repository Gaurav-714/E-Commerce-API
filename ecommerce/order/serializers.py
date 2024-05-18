from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    
    order = serializers.SerializerMethodField(method_name='get_order_items', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_order_items(self, obj):
        orderitems = obj.orderitems.all()
        serializer = OrderItemsSerializer(orderitems, many=True)
        return serializer.data