from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.models import User
import stripe.error
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemsSerializer
from .filters import OrderFilter
from product.models import Product, ProductImages
from utils.helpers import get_current_host
import stripe
import os


class PlaceOrderView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            data = request.data
            order_items = data['order_items']
            
            if len(order_items) == 0:
                return Response({
                    'success': False,
                    'error': 'No order items. Please add atleast one product.'
                })
            
            total_amount = 0
            for item in order_items:
                product = Product.objects.get(id=item['product'])
                quantity = item['quantity']

                total_amount += product.price * quantity

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
                product_img = ProductImages.objects.get(id=i['product'])

                item = OrderItem.objects.create(
                    product = product,
                    order = order,
                    name = product.name,
                    quantity = i['quantity'],
                    price = product.price,
                    image = product_img.image
                )
            
                product.stock -= item.quantity
                product.save()

            serializer = OrderSerializer(order, many=False)

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
            user = request.user
            filterset = OrderFilter(request.GET, queryset=Order.objects.filter(user=user).order_by('id'))
            count = filterset.qs.count()

            page_no = request.GET.get('page', 1)
            res_per_page = 1
            paginator = Paginator(filterset.qs, res_per_page)

            serializer = OrderSerializer(paginator.page(page_no), many=True)

            if len(serializer.data) == 0:
                return Response({
                    'success': False,
                    'message': 'You have not ordered anything yet.',
                    'data': []
                }) 

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

            if order.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You cannot view others orders.'
                }) 

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


class CheckoutSessionView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            user = request.user
            order_items = request.data['order_items']
            order_data = Order.objects.get(id=pk)

            stripe.api_key = os.environ.get('STRIPE_PRIVATE_KEY')

            shipping_details = {
                'area': order_data.area,
                'city': order_data.city, 
                'state': order_data.state,
                'country': order_data.country,
                'zip_code': order_data.zip_code,
                'phone_no': order_data.phone_no,
                'user': user.id
            }

            checkout_order_items = []

            for item in order_items:

                product = Product.objects.get(id=item['product'])
                product_img = ProductImages.objects.get(id=item['product'])
                image = 'http://127.0.0.1:8000/api/' + str(product_img.image)
                print(image)

                checkout_order_items.append({
                    'price_data': {
                        'currency': 'INR',
                        'product_data': {
                            'name': product.name,
                            'images': [image],
                            'metadata': {'product_id': item['product']}
                        },
                        'unit_amount': int(product.price * 100)
                    },
                    'quantity': item['quantity'] 
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                metadata=shipping_details,
                line_items=checkout_order_items,
                customer_email=user.email,
                mode='payment',
                success_url='http://127.0.0.1:8000/api/products',
                cancel_url='http://127.0.0.1:8000/api/products'
            )

            return Response({
                'succuss': True,
                'session' : session
            })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': str(ex)
            })
    

class StripeWebhookView(APIView):

    def post(self, request):
        try:
            webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            event = None

            if sig_header is None:
                return Response({'message': 'Missing Stripe Signature Header'}, status=400)

            try:
                event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            except ValueError as ex:
                return Response({'message': 'Invalid Payload', 'error': str(ex)})
            except stripe.error.SignatureVerificationError as ex:
                return Response({'message': 'Invalid Signature', 'error': str(ex)})
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
            
                line_items = stripe.checkout.Session.list_line_items(session['id'])
                price = session['amount_total'] / 100

                order = Order.objects.create(
                    user = User(session.metadata.user),
                    area = session.metadata.area,
                    city = session.metadata.city,
                    state = session.metadata.state,
                    country = session.metadata.country,
                    zip_code = session.metadata.zip_code,
                    phone_no = session.metadata.phone_no,
                    total_amount = price,
                    payment_mode = 'Card',
                    payment_status = 'PAID'
                )

                for item in line_items:
                    
                    line_product = stripe.Product.retrieve(item.price.product)
                    product_id = line_product.metadata.product_id

                    product = Product.objects.get(id=product_id)

                    items = OrderItem.objects.create(
                        product = product,
                        order = order,
                        name = product.name,
                        quantity = item.quantity,
                        price = item.price.unit_amount / 100,
                        image = line_product.images[0]
                    )

                    product.stock -= items.quantity
                    product.save()

                return Response({
                    'success': True,
                    'message': 'Payment Successfull'
                })
        
        except Exception as ex:
            return Response({
                'success': False,
                'message': 'Error occured.',
                'error': str(ex)
            })