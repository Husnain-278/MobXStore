from django.contrib.auth.hashers import PBKDF2PasswordHasher


class FastPBK2PasswordHasher(PBKDF2PasswordHasher):
    iterations= 100000