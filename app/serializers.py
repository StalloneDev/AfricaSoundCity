from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import *


User = get_user_model()



class RegisterUserSerializer(serializers.ModelSerializer):
    email_or_phone = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type':'password'})
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email_or_phone', 'password', 'first_name', 'last_name')

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        if '@' in email_or_phone:
            data['email_or_phone'] = email_or_phone
        else:
            data['email_or_phone'] = email_or_phone
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user



class ArtistesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artistes
        fields = '__all__'


class CentreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centre
        fields = '__all__'


class ArtisteInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisteInvite
        fields = '__all__'


class CategorieArtisteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieArtiste
        fields = '__all__'


class TypeDiffusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeDiffusion
        fields = '__all__'


class TypeSpectacleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeSpectacle
        fields = '__all__'


class SpectacleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spectacle
        fields = '__all__'


class CodeQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeQR
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


class TypeInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeInstrument
        fields = '__all__'


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'


class NomFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NomFormation
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class TypePaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypePaiement
        fields = '__all__'


class ReserverServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReserverService
        fields = '__all__'


class RestaurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restauration
        fields = '__all__'


class ComanderMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComanderMenu
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ReserverFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReserverFormation
        fields = '__all__'