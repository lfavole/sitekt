from common.forms import get_subscription_form

from .models import Child

SubscriptionForm = get_subscription_form("espacecate", Child)
