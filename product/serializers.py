from rest_framework import serializers
from .models import Product, ProductImages, ProductReview


class ProductImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        fields = '__all__'
    

class ProductSerializer(serializers.ModelSerializer):

    images = ProductImagesSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)

    class Meta:
        model = Product
        fields = ['id','name','brand','category','description','price','stock','ratings','user','images','reviews']
        extra_kwargs = {
            'name': { 'required': True },
            'brand': { 'required': True },
            'description': { 'required': True },
            'price': { 'required': True }
        }

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ProductReviewSerializer(reviews, many=True)
        return serializer.data

