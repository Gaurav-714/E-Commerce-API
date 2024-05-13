from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductView(APIView):
    def get(self, request):
        try:
            products = Product.objects.all()
            search_query = request.GET.get('search')

            if search_query:
                products = Product.objects.filter(Q(name__icontains=search_query))

            filterset = ProductFilter(request.GET, queryset=products.order_by('id'))
            serializer = ProductSerializer(filterset.qs, many=True)

            return Response({
                'success': True,
                'data': serializer.data
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': "Something went wrong.",
                'error': str(ex)
            })