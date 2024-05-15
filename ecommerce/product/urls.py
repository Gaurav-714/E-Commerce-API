from django.urls import path
from .views import *

urlpatterns = [
    path('products', ProductsView.as_view()),
    path('product/upload', UploadProductView.as_view()),
    path('product/images', UploadProductImage.as_view()),
    path('product/update/<int:pk>', UpdateProductView.as_view()),
    path('product/delete/<int:pk>', DeleteProductView.as_view()),
]
