from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from app.models import *
from .forms import *
import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from .serializers import RegisterUserSerializer


User = get_user_model()


def is_admin(user):
    return user.is_superuser



class AdminUserCreateAPIView(APIView):
    def get(self, request):
        return render(request, 'administration/createsuper.html')
    
    def post(self, request):
        email_or_phone = request.POST.get('email_or_phone')
        password = request.POST.get('password')

        if not email_or_phone or not password:
            return render(request, 'administration/createsuper.html', {'error': 'Tous les champs sont obligatoires.'})

        if User.objects.filter(email_or_phone=email_or_phone).exists():
            return render(request, 'administration/createsuper.html', {'error': 'Ce nom d\'utilisateur est déjà pris.'})

        user = User.objects.create_user(email_or_phone=email_or_phone, password=password)
        user.is_admin = True  # Définir l'utilisateur comme administrateur
        user.save()

        return render(request, 'administration/createsuper.html', {'success': 'Compte administrateur créé avec succès.'})
    


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    def perform_create(self, serializer):
        is_admin = self.request.POST.get('is_admin', False)
        is_artistes = self.request.POST.get('is_artistes', False)
        user = serializer.save()
        user.is_admin = is_admin == 'on'
        user.is_artistes = is_artistes == 'on'
        user.save()
        self.send_registration_email(user)

    def send_registration_email(self, user):
        
        pass

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return render(request, 'administration/createsuper.html', {'success': 'Compte administrateur créé avec succès.'})



def login(request):
    if request.POST:
        email_or_phone = request.POST['email_or_phone']
        password = request.POST['password']
        user = authenticate(request, email_or_phone=email_or_phone, password=password)
        if user is not None:
            login_auth(request, user)
            return redirect('administration')
        else:
            return render(request, 'administration/pages/login.html', {'error_message': "Nom d'utilisateur ou mot de passe incorrect."})
    else:
        return render(request, 'administration/pages/login.html')


def request_password(request):
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    symbols = "!@#$%^&*()."
    string = lower + upper + numbers + symbols
    length = 10

    generate_password = "".join(random.sample(string, length))
    return generate_password



class ResetPasswordAPIView(APIView):
    def get(self, request):
        return render(request, 'administration/pages/request_password.html')

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'L\'email est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Aucun utilisateur avec cet email.'}, status=status.HTTP_404_NOT_FOUND)

        # Générer un code de connexion aléatoire en utilisant la fonction request_password
        code = request_password(request)

        # Envoyer l'email avec le code de connexion
        subject = 'Réinitialisation de votre mot de passe'
        message = f'Votre code de connexion est : {code}'
        from_email = 'jenniferstallone8@gmail.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # Enregistrer le code de connexion dans l'objet utilisateur
        user.password_reset_code = code
        user.save()

        return Response({'success': 'Un code de connexion a été envoyé à votre adresse email.'}, status=status.HTTP_200_OK)



class ConfirmResetPasswordAPIView(APIView):
    def get(self, request):
        return render(request, 'administration/pages/confirm_reset_password.html')

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not email or not code or not new_password:
            return Response({'error': 'Tous les champs sont obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, password_reset_code=code)
        except User.DoesNotExist:
            return Response({'error': 'Code de réinitialisation invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.password_reset_code = None
        user.save()

        return Response({'success': 'Votre mot de passe a été réinitialisé avec succès.'}, status=status.HTTP_200_OK)
    
    
    
@login_required(login_url='login')
def administration(request):
    context = {
        'artistes_count': Artistes.objects.count(),
        'centre_count': Centre.objects.count(),
        'artisteInvite_count': ArtisteInvite.objects.count(),
        'categorieArtiste_count': CategorieArtiste.objects.count(),
        'typeDiffusion_count': TypeDiffusion.objects.count(),
        'typeSpectacle_count': TypeSpectacle.objects.count(),
        'spectacle_count': Spectacle.objects.count(),
        'codeQR_count': CodeQR.objects.count(),
        'prochainConcert_count': ProchainConcert.objects.count(),
        'reservation_count': Reservation.objects.count(),
        'typeInstrument_count': TypeInstrument.objects.count(),
        'instrument_count': Instrument.objects.count(),
        'nomFormation_count': NomFormation.objects.count(),
        'service_count': Service.objects.count(),
        'typePaiement_count': TypePaiement.objects.count(),
        'reserverService_count': ReserverService.objects.count(),
        'restauration_count': Restauration.objects.count(),
        'comanderMenu_count': ComanderMenu.objects.count(),
        'payment_count': Payment.objects.count(),
        'reserverFormation_count': ReserverFormation.objects.count(),
    }
    return render(request, 'administration/pages/index.html', context)



# Vues pour Artistes
def ArtistesList(request):
    artistes = Artistes.objects.all()
    context = {'artistes': artistes}
    return render(request, 'administration/pages/Artistes/ArtistesList.html', context)

def ArtistesCreate(request):
    if request.method == 'POST':
        form = ArtistesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ArtistesList')
    else:
        form = ArtistesForm()
    context = {'form': form}
    return render(request, 'administration/pages/Artistes/ArtistesCreate.html', context)

def ArtistesUpdate(request, pk):
    artistes = get_object_or_404(Artistes, pk=pk)
    if request.method == 'POST':
        form = ArtistesForm(request.POST, request.FILES, instance=artistes)
        if form.is_valid():
            form.save()
            return redirect('ArtistesList')
    else:
        form = ArtistesForm(instance=artistes)
    context = {'form': form}
    return render(request, 'administration/pages/Artistes/ArtistesUpdate.html', context)

def ArtistesDelete(request, pk):
    artistes = get_object_or_404(Artistes, pk=pk)
    if request.method == 'POST':
        carrousel.delete()
        return redirect('ArtisteslList')
    context = {'artistes': artistes}
    return render(request, 'administration/pages/Artistes/ArtistesDelete.html', context)


# Vues pour le Centre
def CentreList(request):
    centre = Centre.objects.all()
    context = {'centre': centre}
    return render(request, 'administration/pages/Centre/CentreList.html', context)

def CentreCreate(request):
    if request.method == 'POST':
        form = CentreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('CentreList')
    else:
        form = CentreForm()
    context = {'form': form}
    return render(request, 'administration/pages/Centre/CentreCreate.html', context)

def CentreUpdate(request, pk):
    centre = get_object_or_404(Centre, pk=pk)
    if request.method == 'POST':
        form = CentreForm(request.POST, instance=centre)
        if form.is_valid():
            form.save()
            return redirect('CentreList')
    else:
        form = CentreForm(instance=centre)
    context = {'form': form}
    return render(request, 'administration/pages/Centre/CentreUpdate.html', context)

def CentreDelete(request, pk):
    centre = get_object_or_404(Centre, pk=pk)
    if request.method == 'POST':
        centre.delete()
        return redirect('CentreList')
    context = {'centre': centre}
    return render(request, 'administration/pages/Centre/CentreDelete.html', context)


# Vue pour les Artistes invites
def ArtisteInviteList(request):
    artisteInvite = ArtisteInvite.objects.all()
    context = {'artisteInvite': artisteInvite}
    return render(request, 'administration/pages/ArtisteInvite/ArtisteInviteList.html', context)

def ArtisteInviteCreate(request):
    if request.method == 'POST':
        form = ArtisteInviteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ArtisteInviteList')
    else:
        form = ArtisteInviteForm()
    context = {'form': form}
    return render(request, 'administration/pages/ArtisteInvite/ArtisteInviteCreate.html', context)

def ArtisteInviteUpdate(request, pk):
    artisteInvite = get_object_or_404(ArtisteInvite, pk=pk)
    if request.method == 'POST':
        form = ArtisteInviteForm(request.POST, instance=ArtisteInvite)
        if form.is_valid():
            form.save()
            return redirect('ArtisteInviteList')
    else:
        form = ArtisteInviteForm(instance=artisteInvite)
    context = {'form': form}
    return render(request, 'administration/pages/ArtisteInvite/ArtisteInviteUpdate.html', context)

def ArtisteInviteDelete(request, pk):
    artisteInvite = get_object_or_404(ArtisteInvite, pk=pk)
    if request.method == 'POST':
        artisteInvite.delete()
        return redirect('ArtisteInviteList')
    context = {'artisteInvite': artisteInvite}
    return render(request, 'administration/pages/ArtisteInvite/ArtisteInviteDelete.html', context)


# Vue pour les Catedories d'artistes 
def CategorieArtisteList(request):
    categorieArtiste = CategorieArtiste.objects.all()
    context = {'categorieArtiste': categorieArtiste}
    return render(request, 'administration/pages/CategorieArtiste/CategorieArtisteList.html', context)

def CategorieArtisteCreate(request):
    if request.method == 'POST':
        form = CategorieArtisteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('CategorieArtisteList')
    else:
        form = CategorieArtisteForm()
    context = {'form': form}
    return render(request, 'administration/pages/CategorieArtiste/CategorieArtisteCreate.html', context)

def CategorieArtisteUpdate(request, pk):
    categorieArtiste = get_object_or_404(CategorieArtiste, pk=pk)
    if request.method == 'POST':
        form = CategorieArtisteForm(request.POST, instance=CategorieArtiste)
        if form.is_valid():
            form.save()
            return redirect('CategorieArtisteList')
    else:
        form = CategorieArtisteForm(instance=categorieArtiste)
    context = {'form': form}
    return render(request, 'administration/pages/CategorieArtiste/CategorieArtisteUpdate.html', context)

def CategorieArtisteDelete(request, pk):
    categorieArtiste = get_object_or_404(CategorieArtiste, pk=pk)
    if request.method == 'POST':
        categorieArtiste.delete()
        return redirect('CategorieArtisteList')
    context = {'categorieArtiste': categorieArtiste}
    return render(request, 'administration/pages/CategorieArtiste/CategorieArtisteDelete.html', context)


# Vue pour les Types de diffussion 
def TypeDiffusionList(request):
    typeDiffusion = TypeDiffusion.objects.all()
    context = {'typeDiffusion': typeDiffusion}
    return render(request, 'administration/pages/TypeDiffusion/TypeDiffusionList.html', context)

def TypeDiffusionCreate(request):
    if request.method == 'POST':
        form = TypeDiffusionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('TypeDiffusionList')
    else:
        form = TypeDiffusionForm()
    context = {'form': form}
    return render(request, 'administration/pages/TypeDiffusion/TypeDiffusionCreate.html', context)

def TypeDiffusionUpdate(request, pk):
    typeDiffusion = get_object_or_404(TypeDiffusion, pk=pk)
    if request.method == 'POST':
        form = TypeDiffusionForm(request.POST, instance=TypeDiffusion)
        if form.is_valid():
            form.save()
            return redirect('TypeDiffusionList')
    else:
        form = TypeDiffusionForm(instance=typeDiffusion)
    context = {'form': form}
    return render(request, 'administration/pages/TypeDiffusion/TypeDiffusionUpdate.html', context)

def TypeDiffusionDelete(request, pk):
    typeDiffusion = get_object_or_404(TypeDiffusion, pk=pk)
    if request.method == 'POST':
        typeDiffusion.delete()
        return redirect('TypeDiffusionList')
    context = {'typeDiffusion': typeDiffusion}
    return render(request, 'administration/pages/TypeDiffusion/TypeDiffusionDelete.html', context)


# Vue pour les Types de spectacle
def TypeSpectacleList(request):
    typeSpectacle = TypeSpectacle.objects.all()
    context = {'typeSpectacle': typeSpectacle}
    return render(request, 'administration/pages/TypeSpectacle/TypeSpectacleList.html', context)

def TypeSpectacleCreate(request):
    if request.method == 'POST':
        form = TypeSpectacleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('TypeSpectacleList')
    else:
        form = TypeSpectacleForm()
    context = {'form': form}
    return render(request, 'administration/pages/TypeSpectacle/TypeSpectacleCreate.html', context)

def TypeSpectacleUpdate(request, pk):
    typeSpectacle = get_object_or_404(TypeSpectacle, pk=pk)
    if request.method == 'POST':
        form = TypeSpectacleForm(request.POST, instance=TypeSpectacle)
        if form.is_valid():
            form.save()
            return redirect('TypeSpectacleList')
    else:
        form = TypeSpectacleForm(instance=typeSpectacle)
    context = {'form': form}
    return render(request, 'administration/pages/TypeSpectacle/TypeSpectacleUpdate.html', context)

def TypeSpectacleDelete(request, pk):
    typeSpectacle = get_object_or_404(TypeSpectacle, pk=pk)
    if request.method == 'POST':
        typeSpectacle.delete()
        return redirect('TypeSpectacleList')
    context = {'typeSpectacle': typeSpectacle}
    return render(request, 'administration/pages/TypeSpectacle/TypeSpectacleDelete.html', context)


# Vue pour les Spectacles
def SpectacleList(request):
    spectacle = Spectacle.objects.all()
    context = {'spectacle': spectacle}
    return render(request, 'administration/pages/Spectacle/SpectacleList.html', context)

def SpectacleCreate(request):
    if request.method == 'POST':
        form = SpectacleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SpectacleList')
    else:
        form = SpectacleForm()
    context = {'form': form}
    return render(request, 'administration/pages/Spectacle/SpectacleCreate.html', context)

def SpectacleUpdate(request, pk):
    spectacle = get_object_or_404(Spectacle, pk=pk)
    if request.method == 'POST':
        form = SpectacleForm(request.POST, instance=Spectacle)
        if form.is_valid():
            form.save()
            return redirect('SpectacleList')
    else:
        form = SpectacleForm(instance=spectacle)
    context = {'form': form}
    return render(request, 'administration/pages/Spectacle/SpectacleUpdate.html', context)

def SpectacleDelete(request, pk):
    spectacle = get_object_or_404(Spectacle, pk=pk)
    if request.method == 'POST':
        spectacle.delete()
        return redirect('SpectacleList')
    context = {'spectacle': spectacle}
    return render(request, 'administration/pages/Spectacle/SpectacleDelete.html', context)


# Vue pour les Spectacles
def CodeQRList(request):
    codeQR = CodeQR.objects.all()
    context = {'codeQR': codeQR}
    return render(request, 'administration/pages/CodeQR/CodeQRList.html', context)

def CodeQRCreate(request):
    if request.method == 'POST':
        form = CodeQRForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('CodeQRList')
    else:
        form = CodeQRForm()
    context = {'form': form}
    return render(request, 'administration/pages/CodeQR/CodeQRCreate.html', context)

def CodeQRUpdate(request, pk):
    codeQR = get_object_or_404(CodeQR, pk=pk)
    if request.method == 'POST':
        form = CodeQRForm(request.POST, instance=CodeQR)
        if form.is_valid():
            form.save()
            return redirect('CodeQRList')
    else:
        form = CodeQRForm(instance=codeQR)
    context = {'form': form}
    return render(request, 'administration/pages/CodeQR/CodeQRUpdate.html', context)

def CodeQRDelete(request, pk):
    codeQR = get_object_or_404(CodeQR, pk=pk)
    if request.method == 'POST':
        codeQR.delete()
        return redirect('CodeQRList')
    context = {'codeQR': codeQR}
    return render(request, 'administration/pages/CodeQR/CodeQRDelete.html', context)



# Vue pour le Prochain Concert
def ProchainConcertList(request):
    prochainConcert = ProchainConcert.objects.all()
    context = {'prochainConcert': prochainConcert}
    return render(request, 'administration/pages/ProchainConcert/ProchainConcertList.html', context)

def ProchainConcertCreate(request):
    if request.method == 'POST':
        form = ProchainConcert(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ProchainConcertList')
    else:
        form = ProchainConcert()
    context = {'form': form}
    return render(request, 'administration/pages/ProchainConcert/ProchainConcertCreate.html', context)

def ProchainConcertUpdate(request, pk):
    prochainConcert = get_object_or_404(ProchainConcert, pk=pk)
    if request.method == 'POST':
        form = ProchainConcert(request.POST, instance=ProchainConcert)
        if form.is_valid():
            form.save()
            return redirect('ProchainConcertList')
    else:
        form = ProchainConcertForm(instance=prochainConcert)
    context = {'form': form}
    return render(request, 'administration/pages/ProchainConcert/ProchainConcertUpdate.html', context)

def ProchainConcertDelete(request, pk):
    prochainConcert = get_object_or_404(ProchainConcert, pk=pk)
    if request.method == 'POST':
        prochainConcert.delete()
        return redirect('ProchainConcertList')
    context = {'prochainConcert': prochainConcert}
    return render(request, 'administration/pages/ProchainConcert/ProchainConcertDelete.html', context)


# Vue pour la Reservation
def ReservationList(request):
    reservation = Reservation.objects.all()
    context = {'reservation': reservation}
    return render(request, 'administration/pages/Reservation/ReservationList.html', context)

def ReservationCreate(request):
    if request.method == 'POST':
        form = Reservation(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ReservationList')
    else:
        form = Reservation()
    context = {'form': form}
    return render(request, 'administration/pages/Reservation/ReservationCreate.html', context)

def ReservationUpdate(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        form = Reservation(request.POST, instance=Reservation)
        if form.is_valid():
            form.save()
            return redirect('ReservationList')
    else:
        form = ReservationForm(instance=reservation)
    context = {'form': form}
    return render(request, 'administration/pages/Reservation/ReservationUpdate.html', context)

def ReservationDelete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        reservation.delete()
        return redirect('ReservationList')
    context = {'reservation': reservation}
    return render(request, 'administration/pages/Reservation/ReservationDelete.html', context)


# Vue pour le type d'instrument
def TypeInstrumentList(request):
    typeInstrument = TypeInstrument.objects.all()
    context = {'typeInstrument': typeInstrument}
    return render(request, 'administration/pages/TypeInstrument/TypeInstrumentList.html', context)

def TypeInstrumentCreate(request):
    if request.method == 'POST':
        form = TypeInstrument(request.POST)
        if form.is_valid():
            form.save()
            return redirect('TypeInstrumentList')
    else:
        form = TypeInstrument()
    context = {'form': form}
    return render(request, 'administration/pages/TypeInstrument/TypeInstrumentCreate.html', context)

def TypeInstrumentUpdate(request, pk):
    typeInstrument = get_object_or_404(TypeInstrument, pk=pk)
    if request.method == 'POST':
        form = TypeInstrument(request.POST, instance=TypeInstrument)
        if form.is_valid():
            form.save()
            return redirect('TypeInstrumentList')
    else:
        form = TypeInstrumentForm(instance=typeInstrument)
    context = {'form': form}
    return render(request, 'administration/pages/TypeInstrument/TypeInstrumentUpdate.html', context)

def TypeInstrumentDelete(request, pk):
    typeInstrument = get_object_or_404(TypeInstrument, pk=pk)
    if request.method == 'POST':
        TypeInstrument.delete()
        return redirect('TypeInstrumentList')
    context = {'typeInstrument': typeInstrument}
    return render(request, 'administration/pages/TypeInstrument/TypeInstrumentDelete.html', context)


# Vue pour les instruments
def InstrumentList(request):
    instrument = Instrument.objects.all()
    context = {'instrument': instrument}
    return render(request, 'administration/pages/Instrument/InstrumentList.html', context)

def InstrumentCreate(request):
    if request.method == 'POST':
        form = Instrument(request.POST)
        if form.is_valid():
            form.save()
            return redirect('InstrumentList')
    else:
        form = Instrument()
    context = {'form': form}
    return render(request, 'administration/pages/Instrument/InstrumentCreate.html', context)

def InstrumentUpdate(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    if request.method == 'POST':
        form = Instrument(request.POST, instance=Instrument)
        if form.is_valid():
            form.save()
            return redirect('InstrumentList')
    else:
        form = InstrumentForm(instance=instrument)
    context = {'form': form}
    return render(request, 'administration/pages/Instrument/InstrumentUpdate.html', context)

def InstrumentDelete(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    if request.method == 'POST':
        Instrument.delete()
        return redirect('InstrumentList')
    context = {'instrument': instrument}
    return render(request, 'administration/pages/Instrument/InstrumentDelete.html', context)


# Vue pour les noms de formation
def NomFormationList(request):
    nomFormation = NomFormation.objects.all()
    context = {'nomFormation': nomFormation}
    return render(request, 'administration/pages/NomFormation/NomFormationList.html', context)

def NomFormationCreate(request):
    if request.method == 'POST':
        form = NomFormation(request.POST)
        if form.is_valid():
            form.save()
            return redirect('NomFormationList')
    else:
        form = NomFormation()
    context = {'form': form}
    return render(request, 'administration/pages/NomFormation/NomFormationCreate.html', context)

def NomFormationUpdate(request, pk):
    nomFormation = get_object_or_404(NomFormation, pk=pk)
    if request.method == 'POST':
        form = NomFormation(request.POST, instance=NomFormation)
        if form.is_valid():
            form.save()
            return redirect('NomFormationList')
    else:
        form = NomFormationForm(instance=nomFormation)
    context = {'form': form}
    return render(request, 'administration/pages/NomFormation/NomFormationUpdate.html', context)

def NomFormationDelete(request, pk):
    nomFormation = get_object_or_404(NomFormation, pk=pk)
    if request.method == 'POST':
        NomFormation.delete()
        return redirect('NomFormationList')
    context = {'nomFormation': nomFormation}
    return render(request, 'administration/pages/NomFormation/NomFormationDelete.html', context)


# Vue pour les Services
def ServiceList(request):
    service = Service.objects.all()
    context = {'service': service}
    return render(request, 'administration/pages/Service/ServiceList.html', context)

def ServiceCreate(request):
    if request.method == 'POST':
        form = Service(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ServiceList')
    else:
        form = Service()
    context = {'form': form}
    return render(request, 'administration/pages/Service/ServiceCreate.html', context)

def ServiceUpdate(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = Service(request.POST, instance=Service)
        if form.is_valid():
            form.save()
            return redirect('ServiceList')
    else:
        form = ServiceForm(instance=service)
    context = {'form': form}
    return render(request, 'administration/pages/Service/ServiceUpdate.html', context)

def ServiceDelete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        Service.delete()
        return redirect('ServiceList')
    context = {'service': service}
    return render(request, 'administration/pages/Service/ServiceDelete.html', context)


# Vue pour les Types de Paiement
def TypePaiementList(request):
    typePaiement = TypePaiement.objects.all()
    context = {'typePaiement': typePaiement}
    return render(request, 'administration/pages/TypePaiement/TypePaiementList.html', context)

def TypePaiementCreate(request):
    if request.method == 'POST':
        form = TypePaiement(request.POST)
        if form.is_valid():
            form.save()
            return redirect('TypePaiementList')
    else:
        form = TypePaiement()
    context = {'form': form}
    return render(request, 'administration/pages/TypePaiement/TypePaiementCreate.html', context)

def TypePaiementUpdate(request, pk):
    typePaiement = get_object_or_404(TypePaiement, pk=pk)
    if request.method == 'POST':
        form = TypePaiement(request.POST, instance=TypePaiement)
        if form.is_valid():
            form.save()
            return redirect('TypePaiementList')
    else:
        form = TypePaiementForm(instance=typePaiement)
    context = {'form': form}
    return render(request, 'administration/pages/TypePaiement/TypePaiementUpdate.html', context)

def TypePaiementDelete(request, pk):
    typePaiement = get_object_or_404(TypePaiement, pk=pk)
    if request.method == 'POST':
        TypePaiement.delete()
        return redirect('TypePaiementList')
    context = {'typePaiement': typePaiement}
    return render(request, 'administration/pages/TypePaiement/TypePaiementDelete.html', context)


# Vue pour les Reservations de Services
def ReserverServiceList(request):
    reserverService = ReserverService.objects.all()
    context = {'reserverService': reserverService}
    return render(request, 'administration/pages/ReserverService/ReserverServiceList.html', context)

def ReserverServiceCreate(request):
    if request.method == 'POST':
        form = ReserverService(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ReserverServiceList')
    else:
        form = ReserverService()
    context = {'form': form}
    return render(request, 'administration/pages/ReserverService/ReserverServiceCreate.html', context)

def ReserverServiceUpdate(request, pk):
    reserverService = get_object_or_404(ReserverService, pk=pk)
    if request.method == 'POST':
        form = ReserverService(request.POST, instance=ReserverService)
        if form.is_valid():
            form.save()
            return redirect('ReserverServiceList')
    else:
        form = ReserverServiceForm(instance=reserverService)
    context = {'form': form}
    return render(request, 'administration/pages/ReserverService/ReserverServiceUpdate.html', context)

def ReserverServiceDelete(request, pk):
    reserverService = get_object_or_404(ReserverService, pk=pk)
    if request.method == 'POST':
        ReserverService.delete()
        return redirect('ReserverServiceList')
    context = {'reserverService': reserverService}
    return render(request, 'administration/pages/ReserverService/ReserverServiceDelete.html', context)


# Vue pour la Restauration
def RestaurationList(request):
    restauration = Restauration.objects.all()
    context = {'restauration': restauration}
    return render(request, 'administration/pages/Restauration/RestaurationList.html', context)

def RestaurationCreate(request):
    if request.method == 'POST':
        form = Restauration(request.POST)
        if form.is_valid():
            form.save()
            return redirect('RestaurationList')
    else:
        form = Restauration()
    context = {'form': form}
    return render(request, 'administration/pages/Restauration/RestaurationCreate.html', context)

def RestaurationUpdate(request, pk):
    restauration = get_object_or_404(Restauration, pk=pk)
    if request.method == 'POST':
        form = Restauration(request.POST, instance=Restauration)
        if form.is_valid():
            form.save()
            return redirect('RestaurationList')
    else:
        form = RestaurationForm(instance=restauration)
    context = {'form': form}
    return render(request, 'administration/pages/Restauration/RestaurationUpdate.html', context)

def RestaurationDelete(request, pk):
    restauration = get_object_or_404(Restauration, pk=pk)
    if request.method == 'POST':
        Restauration.delete()
        return redirect('RestaurationList')
    context = {'restauration': restauration}
    return render(request, 'administration/pages/Restauration/RestaurationDelete.html', context)


# Vue pour commander un menu
def ComanderMenuList(request):
    comanderMenu = ComanderMenu.objects.all()
    context = {'comanderMenu': comanderMenu}
    return render(request, 'administration/pages/ComanderMenu/ComanderMenuList.html', context)

def ComanderMenuCreate(request):
    if request.method == 'POST':
        form = ComanderMenu(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ComanderMenuList')
    else:
        form = ComanderMenu()
    context = {'form': form}
    return render(request, 'administration/pages/ComanderMenu/ComanderMenuCreate.html', context)

def ComanderMenuUpdate(request, pk):
    comanderMenu = get_object_or_404(ComanderMenu, pk=pk)
    if request.method == 'POST':
        form = ComanderMenu(request.POST, instance=ComanderMenu)
        if form.is_valid():
            form.save()
            return redirect('ComanderMenuList')
    else:
        form = ComanderMenuForm(instance=comanderMenu)
    context = {'form': form}
    return render(request, 'administration/pages/ComanderMenu/ComanderMenuUpdate.html', context)

def ComanderMenuDelete(request, pk):
    comanderMenu = get_object_or_404(ComanderMenu, pk=pk)
    if request.method == 'POST':
        ComanderMenu.delete()
        return redirect('ComanderMenuList')
    context = {'comanderMenu': comanderMenu}
    return render(request, 'administration/pages/ComanderMenu/ComanderMenuDelete.html', context)


# Vue pour les Payment
def PaymentList(request):
    payment = Payment.objects.all()
    context = {'payment': payment}
    return render(request, 'administration/pages/Payment/PaymentList.html', context)

def PaymentCreate(request):
    if request.method == 'POST':
        form = Payment(request.POST)
        if form.is_valid():
            form.save()
            return redirect('PaymentList')
    else:
        form = Payment()
    context = {'form': form}
    return render(request, 'administration/pages/Payment/PaymentCreate.html', context)

def PaymentUpdate(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = Payment(request.POST, instance=Payment)
        if form.is_valid():
            form.save()
            return redirect('PaymentList')
    else:
        form = PaymentForm(instance=payment)
    context = {'form': form}
    return render(request, 'administration/pages/Payment/PaymentUpdate.html', context)

def PaymentDelete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        Payment.delete()
        return redirect('PaymentList')
    context = {'payment': payment}
    return render(request, 'administration/pages/Payment/PaymentDelete.html', context)


# Vue pour Reserver une Formation
def ReserverFormationList(request):
    reserverFormation = ReserverFormation.objects.all()
    context = {'reserverFormation': reserverFormation}
    return render(request, 'administration/pages/ReserverFormation/ReserverFormationList.html', context)

def ReserverFormationCreate(request):
    if request.method == 'POST':
        form = ReserverFormation(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ReserverFormationList')
    else:
        form = ReserverFormation()
    context = {'form': form}
    return render(request, 'administration/pages/ReserverFormation/ReserverFormationCreate.html', context)

def ReserverFormationUpdate(request, pk):
    reserverFormation = get_object_or_404(ReserverFormation, pk=pk)
    if request.method == 'POST':
        form = ReserverFormation(request.POST, instance=ReserverFormation)
        if form.is_valid():
            form.save()
            return redirect('ReserverFormationList')
    else:
        form = ReserverFormationForm(instance=reserverFormation)
    context = {'form': form}
    return render(request, 'administration/pages/ReserverFormation/ReserverFormationUpdate.html', context)

def ReserverFormationDelete(request, pk):
    reserverFormation = get_object_or_404(ReserverFormation, pk=pk)
    if request.method == 'POST':
        ReserverFormation.delete()
        return redirect('ReserverFormationList')
    context = {'reserverFormation': reserverFormation}
    return render(request, 'administration/pages/ReserverFormation/ReserverFormationDelete.html', context)