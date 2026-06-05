from django.shortcuts import render, redirect, get_object_or_400
from django.views.decorators.http import require_POST
from products.models import Product, OrderItem, Order, Stripe
from .cart import Cart
from cart.cart import Cart
from django.conf import settings

# Create your views here.

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_400(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'pdv/index_detail.html', {'cart': cart})

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # FORM PARA VALIDAÇÃO, SIMPLIFICANDO PARA FINS DIDÁTICOS
        order = Order.objects.create (
            first_name=request.POST.get('first_name'),
            surname=request.POST.get('surname'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
        )
    # TRANSFERIR OS ITENS DO CARRINHO DA SESSÃO PARA O BANCO DE DADOS
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            price=item['price'],
            quantity=item['quantity'],
        )
    # FUNÇÃO: LIMPAR O CARRINHO DA SESSÃO
    cart.clear()
    # SESSÃO DE CHECKOUT DO STRIPE (GATEWAY DE PAGAMENTO)
    session_data = {
        'mode': 'payment',
        'success_url': request.build_absolute_uri('/orders/success/'),
        'cancel_url': request.build_absolute_uri('/orders/cancel/'),
        'line_items': [],
    }
    # FUNÇÃO: ADICIONAR OS ITENS DO PEDIDO NO FORMATO EXIGIDO DO STRIPE
    for item in order.items.all():
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(item.price * 100), # O STRIPE RECEBE EM CENTAVOS
                'currency': 'brl', # MOEDA
                'product_data': {'name: item.product.name'},
            }
        })
        checkout_session = Stripe.checkout.Session.create(**session_data)
        # FUNÇÃO: REDIRECIONAR O CLIENTE DIRETAMENTE PARA A PÁGINA DE PAGAMENTO DO STRIPE
        return redirect(checkout_session.url, code=303)
    return render(request, 'orders/index_create.html', {'cart': cart})
