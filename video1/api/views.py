from django.db.models import Max
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import InStockFilterBackend, OrderFilter, ProductFilter
from .models import Order, OrderItem, Product
from .serializers import (OrderItemSerializer, OrderSerializer,
                          ProductInfoSerializer, ProductSerializer, OrderCreateSerializer)


class ProductListCreateApiView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk')
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend,
        ]
    search_fields = ['=name', 'description']  
    ordering_fields = ['price', 'name', 'stock']
    pagination_class = LimitOffsetPagination 
    # pagination_class.page_size = 2  
    # pagination_class.page_query_param = 'pagenum'
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = 4
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ProductDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
    lookup_url_kwarg = 'product_id'
    
    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated] 
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    
    # @action(
    #     detail=False, 
    #     methods=['get'], 
    #     url_path="user_orders",
    #     permission_classes= [IsAuthenticated])
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)
    
    

# class OrderListApiView(generics.ListAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
    
# class UserOrderListApiView(generics.ListAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [
#         IsAuthenticated
#     ]
    
#     def get_queryset(self):
#         qs = super().get_queryset()
#         return qs.filter(user=self.request.user)

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products,  
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price']
        })
        return Response(serializer.data) 

