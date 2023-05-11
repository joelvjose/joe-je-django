import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from carts.models import CartItems
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from products.models import Product
from joejee.models import AddressBook
import datetime

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
# Create your views here.

def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user= request.user, is_ordered = False , order_number = body['orderID'])
    payment = Payment(
        user= request.user,
        payment_id =body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_items = CartItems.objects.filter(user = request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        cart_item = CartItems.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        # reduce quantity in stocsk
        product = Product.objects.get(id=item.product_id) 
        product.stock -= item.quantity
        product.save()
        
        # clear cart
    CartItems.objects.filter(user=request.user).delete()
    
    # order confirmation email
    mail_subject = 'Thank you for your Order!'
    message = render_to_string( 'joejee/order_recieved_email.html', {
        'user': request.user,
        'order':order,
        })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
                   
    # send response back via Json
    data ={
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def place_order(request,total=0,quantity=0,):
    current_user = request.user
    cart_items = CartItems.objects.filter(user= current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('joejee:Shop')
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = int(total * 0.04)
    grand_total = total + tax
    
    active_Addr = AddressBook.objects.filter(user=request.user, status = True).first()
      
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data= Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.pincode = form.cleaned_data['pincode']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generating order id for each order
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            data.order_number = current_date + str(data.id)
            data.save()
            
            order = Order.objects.get(user= current_user,is_ordered= False,order_number=data.order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request, 'joejee/payments.html', context)
    return redirect('checkout')
    
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered= True)
        ordered_product = OrderProduct.objects.filter(order_id= order.id)
        
        subtotal =0
        for item in ordered_product:
            subtotal += item.product_price*item.quantity
        
        payment = Payment.objects.get(payment_id=transID)
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal
        }
        return render(request, 'joejee/order_complete.html',context)      
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('joejee:Shop')