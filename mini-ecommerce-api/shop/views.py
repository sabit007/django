from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import ProductFilter
from .models import Category, Order, Product
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for categories.
    Read (list/retrieve) is open to anyone; write requires authentication.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD for products, with search/filter/ordering/pagination.

    - Search:   /api/products/?search=phone            (matches name & description)
    - Filter:   /api/products/?category=1
                /api/products/?price=499.99
                /api/products/?price_min=100&price_max=500
    - Ordering: /api/products/?ordering=price
                /api/products/?ordering=-price
    """

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_date", "stock", "name"]
    ordering = ["-created_date"]


class OrderViewSet(viewsets.ModelViewSet):
    """
    Authenticated users can create orders and view only their own orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only ever see their own orders.
        return Order.objects.select_related("product", "user").filter(
            user=self.request.user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
