from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, BadHeaderError
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import APIView
import requests
from django.db.models import Q
import config
from .serializers import *
from .models import *
from datetime import datetime, date
from django.views.generic import ListView
from django.utils.timezone import now

from django.urls import reverse
from django.views.generic.base import RedirectView
from django.utils import timezone

from django.http import HttpResponseForbidden
import hmac
import hashlib
from django.http import Http404

from django.utils.translation import activate
from django.http import HttpResponseRedirect
from django.utils import translation
from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotFound

User = get_user_model()

class RegisterUserView(CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_registration_email(user)

    def send_registration_email(self, user):
        subject = 'Bienvenue sur AfricaSoundCity'
        html_message = render_to_string('authentication/registration_email.html', {'user': user})
        plain_message = strip_tags(html_message)
        from_email = 'jenniferstallone8@gmail.com'
        to_email = [user.email_or_phone]
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return render(request, 'authentication/200_registration_email.html', status=200)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterUserSerializer

    def retrieve(self, request, *args, **kwargs):
        user_instance = self.get_object()
        serializer = self.get_serializer(user_instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user_instance = self.get_object()
        serializer = self.get_serializer(user_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = get_user_model().objects.get(pk=user_id)
        user.delete()
        return Response({'message': f'User with ID {user_id} has been deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except get_user_model().DoesNotExist:
        return Response({'message': f'User with ID {user_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def login_view(request):
    if request.method == 'POST':
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')

        user = authenticate(request, email_or_phone=email_or_phone, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return JsonResponse({'message': 'Authentification réussie.', 'redirect_url': '/administration/'})
            else:
                return JsonResponse({'message': 'Authentification réussie.', 'redirect_url': '/'})
        else:
            return JsonResponse({'error': 'Identifiant ou mot de passe incorrect.'}, status=400)
    else:
        return Response({'error': 'La méthode HTTP doit être POST.'}, status=405)


@api_view(['POST'])
def reset_password_email(request):
    if request.method == 'POST':
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uri = urlsafe_base64_encode(force_bytes(user.pk))

        # Construire l'URL complète
        # reset_url = f'http://localhost:8000/reset-password/{uri}/{token}'
        reset_url = request.build_absolute_uri(reverse('reset_password_confirm', kwargs={'uidb64': uri, 'token': token}))

        # Envoyer l'e-mail avec le lien de réinitialisation de mot de passe
        subject = 'Réinitialisation de mot de passe'
        html_message = render_to_string('authentication/reset_message.html', {'reset_url': reset_url, 'email': email})

        from_email = 'jenniferstallone8@gmail.com'
        to_email = [user.email]

        try:
            send_mail(subject, '', from_email, to_email, html_message=html_message, fail_silently=False)
            # return Response({'message': 'Un e-mail de réinitialisation de mot de passe a été envoyé.'}, status=status.HTTP_200_OK)
            return render(request, 'authentication/200_reset_password_email_sent.html')
        except BadHeaderError:
            # return Response({'message': 'Erreur lors de l\'envoi de l\'e-mail.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return render(request, 'authentication/500_reset_password_email_sent.html')
        except (DjangoValidationError, DRFValidationError) as e:
            # return Response({'message': 'Erreur lors de la validation des données.', 'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
            return render(request, 'authentication/400_reset_password_email_sent.html')
    else:
        return Response({'message': 'Méthode non autorisée.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('page_login')
        else:
            form = SetPasswordForm(user)

        return render(request, 'authentication/reset_password_confirm.html', {'form': form, 'uidb64': uidb64, 'token': token})

    else:
        messages.error(request, 'Ce lien de réinitialisation de mot de passe est invalide.')
        return redirect('page_password_email')

    
    
class RendreArtisteView(APIView):
    def post(self, request, user_id):
        # Récupérez les données soumises par l'utilisateur
        serializer = ArtistesSerializer(data=request.data)
        if serializer.is_valid():
            # Créez une instance du modèle Artistes
            artiste = serializer.save(user_id=user_id)
            # Mettez à jour l'utilisateur pour le marquer comme artiste
            user = User.objects.get(pk=user_id)
            user.is_artistes = True
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistesListView(APIView):
    def get(self, request):
        artistes = Artistes.objects.all()  # Récupère tous les artistes
        serializer = ArtistesSerializer(artistes, many=True)  # Sérialise la liste des artistes
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class CentreViewSet(viewsets.ModelViewSet):
    queryset = Centre.objects.all()
    serializer_class = CentreSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    
class ArtisteInviteViewSet(viewsets.ModelViewSet):
    queryset = ArtisteInvite.objects.all()
    serializer_class = ArtisteInviteSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class CategorieArtisteViewSet(viewsets.ModelViewSet):
    queryset = CategorieArtiste.objects.all()
    serializer_class = CategorieArtisteSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class TypeDiffusionViewSet(viewsets.ModelViewSet):
    queryset = TypeDiffusion.objects.all()
    serializer_class = TypeDiffusionSerializer    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class TypeSpectacleViewSet(viewsets.ModelViewSet):
    queryset = TypeSpectacle.objects.all()
    serializer_class = TypeSpectacleSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class SpectacleViewSet(viewsets.ModelViewSet):
    queryset = Spectacle.objects.all()
    serializer_class = SpectacleSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class CodeQRListCreateAPIView(generics.ListCreateAPIView):
    queryset = CodeQR.objects.all()
    serializer_class = CodeQRSerializer

class CodeQRRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CodeQR.objects.all()
    serializer_class = CodeQRSerializer



class GenererCodeQRView(generics.CreateAPIView):
    queryset = Spectacle.objects.all()
    serializer_class = SpectacleSerializer

    def post(self, request, *args, **kwargs):
        spectacle = self.get_object()
        code_qr = spectacle.generer_code_qr()
        serializer = CodeQRSerializer(code_qr)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def delete(self, request, *args, **kwargs):
        spectacle = self.get_object()
        code_qr = spectacle.code_qr
        if code_qr:
            code_qr.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        spectacle = self.get_object()
        code_qr = spectacle.code_qr
        if code_qr:
            serializer = CodeQRSerializer(code_qr)
            return Response(serializer.data)
        else:
            rcode_qr = spectacle.generer_code_qr()
            serializer = CodeQRSerializer(code_qr)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


def regenerate_qr_codes(request):
    CodeQR.objects.all().delete()

    for spectacle in Spectacle.objects.all():
        spectacle.generer_code_qr()

    return HttpResponse("Codes QR régénérés avec succès.")



class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class TypeInstrumentViewSet(viewsets.ModelViewSet):
    queryset = TypeInstrument.objects.all()
    serializer_class = TypeInstrumentSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class NomFormationViewSet(viewsets.ModelViewSet):
    queryset = NomFormation.objects.all()
    serializer_class = NomFormationSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # formation_data = [formation.serialize() for formation in queryset]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class TypePaiementViewSet(viewsets.ModelViewSet):
    queryset = TypePaiement.objects.all()
    serializer_class = TypePaiementSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ReserverServiceViewSet(viewsets.ModelViewSet):
    queryset = ReserverService.objects.all()
    serializer_class = ReserverServiceSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class RestaurationViewSet(viewsets.ModelViewSet):
    queryset = Restauration.objects.all()
    serializer_class = RestaurationSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComanderMenuViewSet(viewsets.ModelViewSet):
    queryset = ComanderMenu.objects.all()
    serializer_class = ComanderMenuSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)
    
    

class ReserverFormationViewSet(viewsets.ModelViewSet):
    queryset = ReserverFormation.objects.all()
    serializer_class = ReserverFormationSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)





###################    La vue des pages    ###################



def change_language(request, language):
    activate(language_code)
    if language:
        translation.activate(language)
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))




def countdown(request):
    # Récupérer la prochaine date de concert à partir de la base de données
    prochain_evenement = ProchainConcert.objects.select_related('spectacle').first()
    return render(request, 'countdown.html', {'prochain_evenement': prochain_evenement,})



def home(request):
    
    api_url_spectacles = 'http://localhost:8000/app/spectacle/'
    response_spectacles = requests.get(api_url_spectacles)
    
    if response_spectacles.status_code == 200:
        spectacles = response_spectacles.json()
    else:
        spectacles = []
        
    api_url_centres = 'http://localhost:8000/app/centre/'
    response_centres = requests.get(api_url_centres)
    centres = response_centres.json()
    
    prochain_evenement = ProchainConcert.objects.first()
    prochainconcert = ProchainConcert.objects.all()

    context = {
        'spectacles': spectacles,
        'centres': centres,
        'prochain_evenement': prochain_evenement,
        'prochainconcert': prochainconcert,
    }
    
    

    return render(request, 'control_user/pages/index.html', context)




def streamings(request):
    api_url_spectacles = 'http://localhost:8000/app/spectacle/'
    response_spectacles = requests.get(api_url_spectacles)
    
    if response_spectacles.status_code == 200:
        spectacles = response_spectacles.json()
    else:
        spectacles = []

    
    return render(request, 'control_user/pages/streamings.html', {'spectacles': spectacles})



@login_required
def access_streaming(request, spectacle_id):
    spectacle = get_object_or_404(Spectacle, pk=spectacle_id)
    device_info = request.META['HTTP_USER_AGENT']  # Utiliser le user agent comme information sur l'appareil

    if request.method == 'POST':
        code_input = ''.join([
            request.POST.get(f'code_digit_{i}', '') for i in range(1, 7)
        ])
        try:
            code_qr = CodeQR.objects.get(spectacle=spectacle, code_secret=code_input)

            if code_qr.is_used:
                if code_qr.device_info != device_info:
                    error_message = "Ce code secret a déjà été utilisé sur un autre appareil."
                    return render(request, 'control_user/pages/access_streaming.html', {
                        'spectacle': spectacle,
                        'error_message': error_message,
                    })
            else:
                code_qr.is_used = True
                code_qr.device_info = device_info
                code_qr.save()
                success_message = "Votre code est correct."
                return render(request, 'control_user/pages/access_streaming.html', {
                    'spectacle': spectacle,
                    'success_message': success_message,
                    'streaming_url': redirect('streaming_content', spectacle_id=spectacle.id).url,
                })
        except CodeQR.DoesNotExist:
            error_message = "Le code secret est incorrect. Veuillez réessayer."
            return render(request, 'streaming/access_streaming.html', {
                'spectacle': spectacle,
                'error_message': error_message,
            })
    return render(request, 'control_user/pages/access_streaming.html', {'spectacle': spectacle})



def create_kkiapay_session(request, spectacle_id):
    spectacle = Spectacle.objects.get(id=spectacle_id)
    quantity = int(request.GET.get('quantity', 1))
    total_amount = int(spectacle.prix * quantity * 100)
    
    redirect_url = f"https://kkiapay.me/api/paymentlink?amount={total_amount}&apikey={settings.KKIAPAY_API_KEY}&custom_data[spectacle_id]={spectacle.id}&custom_data[quantity]={quantity}&callback_url={request.build_absolute_uri('/webhook/kkiapay/')}"
   
    return redirect(redirect_url)




def envoyer_codes_secrets_par_email(email, tickets_codes, spectacle):
    if len(tickets_codes) == 1:
        sujet = 'Votre code secret pour le streaming payant'
    else:
        sujet = 'Vos codes secrets pour le streaming payant'

    message = render_to_string('control_user/pages/codes_secrets_email.html', {
        'tickets_codes': tickets_codes,
        'spectacle': spectacle,
        'single_ticket': len(tickets_codes) == 1
    })
    destinataires = [email]
    send_mail(sujet, message, None, destinataires)






@csrf_exempt
def kkiapay_webhook(request):
    import json
    payload = json.loads(request.body)
   
    if payload['status'] == 'SUCCESS':
        customer_email = payload.get('customer_email')
        spectacle_id = payload.get('custom_data', {}).get('spectacle_id')
        quantity = int(payload.get('custom_data', {}).get('quantity', 1))
        montant_total = payload.get('amount')
        transaction_id = payload.get('transaction_id')
       
        if customer_email and spectacle_id:
            try:
                spectacle = Spectacle.objects.get(id=spectacle_id)
                
                achat = Achat.objects.create(
                    spectacle=spectacle,
                    user_email=customer_email,
                    quantity=quantity,
                    montant_total=montant_total,
                    transaction_id=transaction_id,
                    statut_paiement='SUCCESS'
                )
                
                tickets_codes = []
                for i in range(quantity):
                    code_qr = spectacle.generer_code_qr()
                    tickets_codes.append({
                        'numero': i + 1,
                        'code': code_qr.code_secret
                    })
                
                envoyer_codes_secrets_par_email(customer_email, tickets_codes, spectacle)
                
            except Spectacle.DoesNotExist:
                return JsonResponse({'status': 'spectacle not found'}, status=404)

    return JsonResponse({'status': 'success'}, status=200)




def service(request):
    
    api_url_formations = 'http://localhost:8000/app/nom_formation/'
    response_formations = requests.get(api_url_formations)
    formations = response_formations.json()
    
    return render(request, 'control_user/pages/service.html', {'formations': formations})



def reservet(request):
    return render(request, 'control_user/pages/reservet.html')


def commander(request):
    return render(request, 'control_user/pages/commander.html')


def ticketdetails(request, spectacle_id):
    api_url_spectacles = f'http://localhost:8000/app/spectacle/{spectacle_id}/'
    response_spectacles = requests.get(api_url_spectacles)

    if response_spectacles.status_code == 200:
        spectacle = response_spectacles.json()
        return render(request, 'control_user/pages/ticketdetails.html', {'spectacle': spectacle})
    else:
        return HttpResponseNotFound('Spectacle not found')




class ShowsListView(ListView):
    template_name = 'control_user/pages/shows.html'
    context_object_name = 'spectacles'

    def get_queryset(self):
        api_url_spectacles = 'http://localhost:8000/app/spectacle/'
        response_spectacles = requests.get(api_url_spectacles)
        spectacles = response_spectacles.json() if response_spectacles.status_code == 200 else []

        type_spectacle_id = self.kwargs.get('type_spectacle_id')

        queryset = []
        for spectacle in spectacles:
            try:
                date_spectacle = datetime.strptime(spectacle.get('date'), '%Y-%m-%d').date()
                if date_spectacle >= date.today():  # Filtrer les spectacles à venir
                    spectacle_data = {
                        'type_spectacle': spectacle.get('type_spectacle'),
                        'nom_spectacle': spectacle.get('nom_spectacle'),
                        'image': spectacle.get('image'),
                        'date': date_spectacle,
                        'lieu': spectacle.get('lieu'),
                        'description': spectacle.get('description'),
                        'ticket_disponible': spectacle.get('ticket_disponible'),
                        'is_gratuit': spectacle.get('is_gratuit'),
                        'prix': spectacle.get('prix'),
                        'heure_debut': spectacle.get('heure_debut'),
                        'heure_fin': spectacle.get('heure_fin'),
                        'is_valid': spectacle.get('is_valid'),
                    }
                    if type_spectacle_id:
                        if str(type_spectacle_id) == str(spectacle_data['type_spectacle']):
                            queryset.append(spectacle_data)
                    else:
                        queryset.append(spectacle_data)
            except Exception as e:
                print(f"Error processing spectacle data: {e}")
                continue

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api_url_typespectacles = 'http://localhost:8000/app/type_spectacle/'
        response_typespectacles = requests.get(api_url_typespectacles)
        typespectacles = response_typespectacles.json() if response_typespectacles.status_code == 200 else []
        context['typespectacles'] = typespectacles

        api_url_spectacles = 'http://localhost:8000/app/spectacle/'
        response_spectacles = requests.get(api_url_spectacles)
        spectacles = response_spectacles.json() if response_spectacles.status_code == 200 else []

        spectacles_passes = []
        for spectacle in spectacles:
            try:
                date_spectacle = datetime.strptime(spectacle.get('date'), '%Y-%m-%d').date()
                if date_spectacle < date.today():  # Filtrer les spectacles passés
                    spectacle_data = {
                        'type_spectacle': spectacle.get('type_spectacle'),
                        'nom_spectacle': spectacle.get('nom_spectacle'),
                        'image': spectacle.get('image'),
                        'date': date_spectacle,
                        'lieu': spectacle.get('lieu'),
                        'description': spectacle.get('description'),
                        'ticket_disponible': spectacle.get('ticket_disponible'),
                        'is_gratuit': spectacle.get('is_gratuit'),
                        'prix': spectacle.get('prix'),
                        'heure_debut': spectacle.get('heure_debut'),
                        'heure_fin': spectacle.get('heure_fin'),
                        'is_valid': spectacle.get('is_valid'),
                    }
                    spectacles_passes.append(spectacle_data)
            except Exception as e:
                print(f"Error processing spectacle data: {e}")
                continue

        context['spectacles_passes'] = spectacles_passes
        context['typespectacles'] = TypeSpectacle.objects.all()
        return context




def restaurant(request):
    
    api_url_restaurants = 'http://localhost:8000/app/restauration/'
    response_restaurants = requests.get(api_url_restaurants)
    
    if response_restaurants.status_code == 200:
        restaurants = response_restaurants.json()
    else:
        restaurants = []
    
    
    return render(request, 'control_user/pages/restaurant.html', {'restaurants': restaurants})



def page_register(request):
    	return render(request, 'authentication/authentication-register.html')


def page_login(request):
	return render(request, 'authentication/authentication-login.html')


def page_password_email(request):
	return render(request, 'authentication/reset_password_email.html')