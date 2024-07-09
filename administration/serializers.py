# administration/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model



User = get_user_model()

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email_or_phone', 'password', 'is_admin', 'is_artistes')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            last_name=validated_data['last_name'],
            first_name=validated_data['first_name'],
            email_or_phone=validated_data['email_or_phone'],
            is_admin=validated_data.get('is_admin', False),
            is_artistes=validated_data.get('is_artistes', False)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
