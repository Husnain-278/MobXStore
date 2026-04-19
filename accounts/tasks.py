from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from urllib.parse import urljoin


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, recipient_email, uidb64, token):
    try:
        frontend_base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        verification_url = urljoin(
            frontend_base_url.rstrip('/') + '/',
            f'verify-email/{uidb64}/{token}/'
        )

        send_mail(
            subject='Verify your Account',
            message=f'Click the link to verify your account:\n{verification_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)