from django.forms import ModelForm
from app.models import *



class ArtistesForm(ModelForm):
    class Meta:
        model = Artistes
        fields = ['nom', 'biographie', 'image']


class CentreForm(ModelForm):
    class Meta:
        model = Centre
        fields = ['nom', 'logo', 'cygle', 'adresse']
        
        
class ArtisteInviteForm(ModelForm):
    class Meta:
        model = ArtisteInvite
        fields = ['nom', 'phone', 'image_artiste']
        
        
class CategorieArtisteForm(ModelForm):
    class Meta:
        model = CategorieArtiste
        fields = ['nom_artiste', 'categorie']
        
        
class TypeDiffusionForm(ModelForm):
    class Meta:
        model = TypeDiffusion
        fields = ['nom', 'is_gratuit']
        
        
class TypeSpectacleForm(ModelForm):
    class Meta:
        model = TypeSpectacle
        fields = ['type', 'is_valid']
        
        
class SpectacleForm(ModelForm):
    class Meta:
        model = Spectacle
        fields = ['type_spectacle', 'nom_spectacle', 'image', 'date', 'lieu', 'description', 
                    'ticket_disponible', 'is_gratuit', 'prix', 'heure_debut', 'heure_fin', 'lien_streaming', 'is_valid']
        

class CodeQRForm(ModelForm):
    class Meta:
        model = CodeQR
        fields = ['spectacle', 'code_qr', 'token']
        

class ProchainConcertForm(ModelForm):
    class Meta:
        model = ProchainConcert
        fields = ['date', 'spectacle']
     
        
class ReservationForm(ModelForm):
    class Meta:
        model = Reservation
        fields = ['nom', 'email', 'spectacle', 'nombre_billets', 'cout_total', 'statut_paiement', 'is_valid']
        
        
class TypeInstrumentForm(ModelForm):
    class Meta:
        model = TypeInstrument
        fields = ['type_instrument']
        
        
class InstrumentForm(ModelForm):
    class Meta:
        model = Instrument
        fields = ['type_instrument', 'nom_instructeur', 'prenom_instructeur']
        
        
class NomFormationForm(ModelForm):
    class Meta:
        model = NomFormation
        fields = ['nom_formation', 'type_instrument', 'image', 'description', 'prix']
        
        
class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ['nom_formation', 'type_formation', 'instrument', 'date_formation']
        
        
class TypePaiementForm(ModelForm):
    class Meta:
        model = TypePaiement
        fields = ['nom']
        
        
class ReserverServiceForm(ModelForm):
    class Meta:
        model = ReserverService
        fields = ['type_paiement', 'nom_formation', 'type_instrument', 'nom', 'prenoms', 
                  'telephone', 'nombre_place', 'date_paiement', 'montant', 'is_valid']
        
        
class RestaurationForm(ModelForm):
    class Meta:
        model = Restauration
        fields = ['menu', 'description', 'image', 'prix']
        
        
class ComanderMenuForm(ModelForm):
    class Meta:
        model = ComanderMenu
        fields = ['type_paiement', 'menu', 'nom', 'prenoms', 'telephone', 'nombre_commande',
                  'date_paiement', 'montant', 'is_valid']
        
        
class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'montant', 'montant_remis', 'relicat']
        
        
class ReserverFormationForm(ModelForm):
    class Meta:
        model = ReserverFormation
        fields = ['nom', 'prenom', 'telephone', 'instrument', 'nombre_de_places', 'montant']
        
        

        
        
