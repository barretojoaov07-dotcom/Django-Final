from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Order

try:
    import importlib
    stripe = importlib.import_module('stripe')
except ImportError:
    stripe = None
from django.conf import settings


@csrf_exempt
def stripe_webhook(request):
    # raw request body and signature header
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None
    try:
        if stripe is None:
            return HttpResponse(status=501)
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    # payment completed
    session = None
    if event.get('type') == 'checkout.session.completed':
        session = event['data'].get('object', {})

    # find corresponding order and mark as paid
    if session:
        order_id = session.get('client_reference_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
            except Order.DoesNotExist:
                # ignore if order not found
                pass
    return HttpResponse(status=200)
