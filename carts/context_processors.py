from .models import CartItems,Cart
from .views import _cart_id

def counter(request):
    cart_count = 0
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        cart_item = CartItems.objects.all().filter(cart= cart[:1])
        for item in cart_item:
            cart_count += item.quantity
    except cart.DoesNotExist:
        cart_count =0
    return dict(cart_count=cart_count)