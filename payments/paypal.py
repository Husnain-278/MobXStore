from django.conf import settings
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment

# Determine PayPal environment based on settings
PAYPAL_ENVIRONMENT = (
    Environment.PRODUCTION
    if settings.PAYPAL_MODE == "production"
    else Environment.SANDBOX
)

paypal_client = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=settings.PAYPAL_CLIENT_ID,
        o_auth_client_secret=settings.PAYPAL_CLIENT_SECRET,
    ),
    environment=PAYPAL_ENVIRONMENT
)