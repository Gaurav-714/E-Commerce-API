from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, ProductImages
from .serializers import ProductSerializer, ProductImagesSerializer
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
                'message': 'Products fetched successfully.',
                'data': serializer.data
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': str(ex)
            })
        

class ProductImageView(APIView):
    def post(self, request):
        try:
            data = request.data
            files = request.FILES.getlist('images')

            images = []
            for file in files:
                image = ProductImages.objects.create(product=Product(data['product']), image=file)
                images.append(image)

            serializer = ProductImagesSerializer(images, many=True)

            return Response({
                'success': True,
                'message': 'Images uploaded successfully.',
                'data': serializer.data
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': str(ex)
            })