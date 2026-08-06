from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user is None or not user.is_superuser:
            raise serializers.ValidationError(
                "Invalid credentials or insufficient privileges."
            )

        tokens = RefreshToken.for_user(user)

        attrs["user"] = user
        attrs["access"] = str(tokens.access_token)
        attrs["refresh"] = str(tokens)

        return attrs