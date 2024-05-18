from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .filters import OrderFilter
from product.models import Product


class PlaceOrderView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data
            order_items = data['order_items']
            
            if order_items and len(order_items) == 0:
                return Response({
                    'success': False,
                    'error': 'No order items. Please add atleast one product.'
                })
            
            total_amount = sum(item['price'] * item['quantity'] for item in order_items)

            order = Order.objects.create(
                user = user,
                area = data['area'],
                city = data['city'],
                state = data['state'],
                zip_code = data['zip_code'],
                phone_no = data['phone_no'],
                country = data['country'],
                total_amount = total_amount
            )

            for i in order_items:
                product = Product.objects.get(id=i['product'])

                item = OrderItem.objects.create(
                    product = product,
                    order = order,
                    name = product.name,
                    quantity = i['quantity'],
                    price = i['price']
                )

                product.stock -= item.quantity
                product.save()

            serializer = OrderSerializer(order)

            return Response({
                'success': True,
                'message': 'Order placed successfully.',
                'data': serializer.data
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured',
                'error': str(ex)
            })
        

class GetAllOrdersView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            filterset = OrderFilter(request.GET, queryset=Order.objects.all().order_by('id'))
            count = filterset.qs.count()

            page_no = request.GET.get('page', 1)
            res_per_page = 1
            paginator = Paginator(filterset.qs, res_per_page)

            serializer = OrderSerializer(paginator.page(page_no), many=True)

            return Response({
                'success': True,
                'message': 'Orders fetched successfully.',
                'count': count,
                'results per page': res_per_page,
                'data': serializer.data
            }) 
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured',
                'error': str(ex)
            })
    

class GetOrderView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk)               
            serializer = OrderSerializer(order)

            return Response({
                'success': True,
                'message': 'Order fetched successfully.',
                'data': serializer.data
            }) 
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured',
                'error': str(ex)
            })


class UpdateOrderView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        try:        
            order = get_object_or_404(Order, id=pk)
            serializer = OrderSerializer(data=request.data, instance=order, many=False, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response({
                    'success': True,
                    'message': 'Order status updated successfully.',
                    'data': serializer.data
                }) 
            
            return Response({
                'success': False,
                'message': 'Error occured',
                'error': serializer.errors
            })
    
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured',
                'error': str(ex)
            })
    

class DeleteOrderView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):

        order = get_object_or_404(Order, id=pk)
        order.delete()

        return Response({
            'success': True,
            'message': 'Order deleted successfully.',
        }) 
