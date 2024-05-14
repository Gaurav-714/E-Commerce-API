from rest_framework import serializers
from .models import Product, ProductImages


class ProductImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    images = ProductImagesSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id','name','brand','category','description','price','stock','user','images']

