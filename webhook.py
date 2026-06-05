from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order
import stripe
from django.conf import settings

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    # PAGAMENTO CONCLUÍDO
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
    # LÓGICA PARA ENCONTRAR O PEDIDO CORRESPONDENTE, FAZENDO COM QUE MARQUE COMO "PAGO"
    order_id = session.get('client_reference_id')
    if order_id:
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()
    return HttpResponse(status=200)
