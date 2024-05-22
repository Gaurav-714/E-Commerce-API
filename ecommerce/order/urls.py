from django.urls import path
from .views import *

urlpatterns = [
    path('order/place', PlaceOrderView.as_view()),
    path('order/view', GetAllOrdersView.as_view()),
    path('order/view/<int:pk>', GetOrderView.as_view()),
    path('order/update/<int:pk>', UpdateOrderView.as_view()),
    path('order/delete/<int:pk>', DeleteOrderView.as_view()),
    path('order/checkout-session/<int:pk>', CheckoutSessionView.as_view()),
    path('order/webhook', StripeWebhookView.as_view()),
]
