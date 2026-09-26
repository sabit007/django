from rest_framework import serializers

from .models import Category, Order, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "stock",
            "category",
            "category_name",
            "created_date",
        ]
        read_only_fields = ["id", "created_date"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "product",
            "product_name",
            "quantity",
            "total_price",
            "order_date",
        ]
        read_only_fields = ["id", "user", "total_price", "order_date"]

    def validate(self, attrs):
        product = attrs.get("product") or getattr(self.instance, "product", None)
        quantity = attrs.get("quantity") or getattr(self.instance, "quantity", None)

        if product is not None and quantity is not None:
            if quantity > product.stock:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            f"Only {product.stock} unit(s) of '{product.name}' "
                            "left in stock."
                        )
                    }
                )
        return attrs

    def create(self, validated_data):
        # Attach the requesting user and atomically decrement stock.
        request = self.context["request"]
        validated_data["user"] = request.user

        product = validated_data["product"]
        quantity = validated_data["quantity"]

        order = Order.objects.create(**validated_data)

        product.stock -= quantity
        product.save(update_fields=["stock"])

        return order
