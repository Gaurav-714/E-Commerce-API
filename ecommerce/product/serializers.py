from rest_framework import serializers
from .models import Product, ProductImages


class ProductImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    images = ProductImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id','name','brand','category','description','price','stock','ratings','user','images']
        extra_kwargs = {
            'name': { 'required': True },
            'brand': { 'required': True },
            'description': { 'required': True },
            'price': { 'required': True }
        }

