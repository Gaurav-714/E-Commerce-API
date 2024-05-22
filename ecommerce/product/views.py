from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Q
from django.db.models import Avg
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import Product, ProductImages, ProductReview
from .serializers import ProductSerializer, ProductImagesSerializer, ProductReviewSerializer
from .filters import ProductFilter


class ProductsView(APIView):
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


class UploadProductView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            data = request.data            
            serializer = ProductSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Product uploaded successfully.',
                    'data': serializer.validated_data
                })
            
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': serializer.errors
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })


class UploadProductImage(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

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
        

class UpdateProductView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:
            product = get_object_or_404(Product, id=pk)
            print(product.user)
            print(request.user)
            if product.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You are not authorized for this.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = ProductSerializer(data=request.data, instance=product, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Product updated successfully.',
                    'data': serializer.validated_data
                })
            
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': serializer.errors
            })

        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })
        

class DeleteProductView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def delete(self, request, pk):
        try:
            product = get_object_or_404(Product, id=pk)
            if product.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You are not authorized for this.'
                }, status=status.HTTP_401_UNAUTHORIZED)

            args = { 'product': pk }
            images = ProductImages.objects.filter(**args)
            for i in images:
                i.delete()

            product.delete()

            return Response({
                'success': True,
                'message': 'Product deleted successfully.'
            })

        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })
        

class ReviewProduct(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            data = request.data

            if data['rating'] <= 0 or data['rating'] > 5:
                return Response({
                    'success': False,
                    'error': 'Please rate from 1 to 5.'
                }, status=status.HTTP_406_NOT_ACCEPTABLE)

            product = get_object_or_404(Product, id=pk)
            review = product.reviews.filter(user=request.user) 

            obj = get_object_or_404(ProductReview, user=request.user.id)
            if obj.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You are not authorized for this.'
                }, status=status.HTTP_401_UNAUTHORIZED)

            if review.exists():
                new_review = { 'review':data['review'], 'rating': data['rating'] } 
                review.update(**new_review)

                rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
                product.rating = rating['avg_ratings']
                product.save()

                return Response({
                    'success': True,
                    'message': 'Review updated successfully.',
                    'data': data
                })

            ProductReview.objects.create(
                user = request.user,
                product = product,
                review = data['review'],
                rating = data['rating']
            )
            rating = product.reviews.aggregate(avg_ratings=Avg('rating'))
            product.rating = rating['avg_ratings']
            product.save()

            return Response({
                'success': True,
                'message': 'Review posted successfully.',
                'data': data
            })
            
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })
        

class DeleteReview(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            product = get_object_or_404(Product, id=pk)
            review = product.reviews.filter(user=request.user)
            print(review)

            if review.exists():
            
                review.delete()

                rating = product.reviews.aggregate(avg_ratings=Avg('rating'))

                if rating['avg_ratings'] is None:
                    product.rating = 0

                product.rating = rating['avg_ratings']
                product.save()

                return Response({
                    'success': True,
                    'message': 'Review deleted successfully.'
                })
            
            return Response({
                'success': False,
                'message': 'Review does not exists.',
            })

        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Something went wrong.',
                'error': str(ex)
            })