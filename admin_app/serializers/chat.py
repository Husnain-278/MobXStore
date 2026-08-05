from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    conversation = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    message = serializers.CharField(
        max_length=5000,
        trim_whitespace=True,
    )

    def validate_message(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value