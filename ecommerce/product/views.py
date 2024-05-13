from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.paginator import Paginator
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
            page_number = request.GET.get('page', 1)
            paginator = Paginator(filterset.qs, 5)
            serializer = ProductSerializer(paginator.page(page_number), many=True)

            return Response({
                'success': True,
                'data': serializer.data
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'error': str(ex)
            })