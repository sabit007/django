from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Order, Product


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")

    def test_anyone_can_list_categories(self):
        Category.objects.create(name="Electronics")
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_requires_auth(self):
        response = self.client.post("/api/categories/", {"name": "Books"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_category(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/categories/", {"name": "Books"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.category = Category.objects.create(name="Electronics")
        Product.objects.create(
            name="iPhone", description="A phone", price=999, stock=5,
            category=self.category,
        )
        Product.objects.create(
            name="Android Phone", description="Another phone", price=499, stock=10,
            category=self.category,
        )

    def test_search_by_name(self):
        response = self.client.get("/api/products/?search=iPhone")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_category(self):
        response = self.client.get(f"/api/products/?category={self.category.id}")
        self.assertEqual(response.data["count"], 2)

    def test_ordering_by_price(self):
        response = self.client.get("/api/products/?ordering=price")
        prices = [item["price"] for item in response.data["results"]]
        self.assertEqual(prices, sorted(prices))


class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.other_user = User.objects.create_user(username="other", password="pass12345")
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="iPhone", description="A phone", price=1000, stock=5,
            category=self.category,
        )

    def test_create_order_requires_auth(self):
        response = self.client.post(
            "/api/orders/", {"product": self.product.id, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_computes_total_and_reduces_stock(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/orders/", {"product": self.product.id, "quantity": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_price"], "2000.00")

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_cannot_order_more_than_stock(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/orders/", {"product": self.product.id, "quantity": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_only_sees_own_orders(self):
        Order.objects.create(user=self.user, product=self.product, quantity=1)
        Order.objects.create(user=self.other_user, product=self.product, quantity=1)

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/orders/")
        self.assertEqual(response.data["count"], 1)
