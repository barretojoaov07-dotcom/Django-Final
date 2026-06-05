from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        # FUNÇÃO: INICIALIZAR O CARRINHO USANDO A SESSÃO DO DJANGO
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False):
        # ADICIONAR UM PRODUTO AO CARRINHO OU UMA QUANTIDADE
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()
    
    def save(self):
        # FUNÇÃO: MARCAR A SESSÃO COMO "MODIFICADA"
        self.session.modified = True
    
    def remove(self, product):
        # FUNÇÃO: REMOVER UM PRODUTO DO CARRINHO
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self):
        # FUNÇÃO: ITERAR OS PRODUTOS DO CARRINHO E BUSCAR OS PRODUTOS DO BANCO DE DADOS
        product_ids = self.cart.keys()
        products = product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        # FUNÇÃO: CONTAR A QUANTIDADE TOTAL DE ITENS DENTRO DO CARRINHO
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        # FUNÇÃO: CALCULAR O VALOR TOTAL DO CARRINHO
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # FUNÇÃO: ESVAZIAR O CARRINHO
        del self.session[settings.CART_SESSION_ID]
        self.save()
