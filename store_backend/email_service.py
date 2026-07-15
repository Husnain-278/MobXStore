import sib_api_v3_sdk

from sib_api_v3_sdk.rest import ApiException

from django.conf import settings


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = settings.BREVO_API_KEY

api_client = sib_api_v3_sdk.ApiClient(configuration)

email_api = sib_api_v3_sdk.TransactionalEmailsApi(api_client)


def send_email(subject, message, recipient):
    email = sib_api_v3_sdk.SendSmtpEmail(
        sender={
            "name": settings.DEFAULT_FROM_NAME,
            "email": settings.DEFAULT_FROM_EMAIL,
        },
        to=[
            {
                "email": recipient,
            }
        ],
        subject=subject,
        text_content=message,
    )

    try:
        email_api.send_transac_email(email)

    except ApiException as e:
        print(e)
        raise