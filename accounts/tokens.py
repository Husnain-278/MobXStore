from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    pass


#class instance
email_verification_token = EmailVerificationTokenGenerator()

