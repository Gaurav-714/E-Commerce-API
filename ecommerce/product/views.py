from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer


class ProductView(APIView):
    def get(self, request):
        products = Product.objects.all()
        search_query = request.GET.get('search')
        if search_query:
            products = Product.objects.filter(Q(name__icontains=search_query))
        serializer = ProductSerializer(products, many=True)
        return Response({
            'products': serializer.data
        })