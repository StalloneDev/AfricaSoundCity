import socket
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, Group, Permission

from django.contrib.auth.signals import user_logged_in
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Module d'import pour la generation et la securisation du code QR
from io import BytesIO
import qrcode
import hmac
import hashlib
from django.core.files import File
from django.utils.text import slugify
import secrets
from django.db import IntegrityError
import string, random


class CustomUserManager(BaseUserManager):
    
    def validate_email_or_phone_unique(self, value):
        # Vérifier si une adresse e-mail ou un numéro de téléphone existe déjà dans la base de données
        if self.model.objects.filter(email_or_phone=value).exists():
            raise ValidationError(
                _('Un utilisateur avec cet email ou numéro de téléphone existe déjà.'),
                params={'value': value},
            )

    def create_user(self, email_or_phone, password=None, **extra_fields):
        if not email_or_phone:
            raise ValueError('L\'adresse e-mail ou le numéro de téléphone est obligatoire pour créer un utilisateur.')

        if '@' in email_or_phone:
            email = self.normalize_email(email_or_phone)
            extra_fields.setdefault('email_or_phone', email)
        else:
            extra_fields.setdefault('email_or_phone', email_or_phone)

        self.validate_email_or_phone_unique(extra_fields['email_or_phone'])

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_or_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email_or_phone, password=password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    email_or_phone = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateTimeField(default=timezone.now)
    last_login_date = models.DateTimeField(null=True, blank=True)
    last_modify_date = models.DateTimeField(null=True, blank=True)
    deactivate_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_artistes = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='user_groups',  # Changez 'user_groups' en ce que vous voulez
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='user_permissions',  # Changez 'user_permissions' en ce que vous voulez
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

    USERNAME_FIELD = "email_or_phone"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email_or_phone


@receiver(post_save, sender=User)
def update_hostname(sender, instance, created, **kwargs):
    if created:
        try:
            instance.hostname = socket.gethostname()
            instance.save()
        except socket.error as e:
            print(f"Erreur lors de la récupération du hostname: {e}")


@receiver(user_logged_in, sender=User)
def update_last_login(sender, user, **kwargs):
    user.last_login_date = timezone.now()
    user.save()


@receiver(pre_save, sender=User)
def update_last_modify(sender, instance, **kwargs):
    instance.last_modify_date = timezone.now()


@receiver(post_save, sender=User)
def update_deactivate_date(sender, instance, **kwargs):
    if not instance.is_active and instance.deactivate_date is None:
        instance.deactivate_date = timezone.now()
        instance.save()


class Artistes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artiste_user')
    nom = models.CharField(max_length=100)
    biographie = models.TextField()
    image = models.ImageField(upload_to='artistes/', null=True, blank=True)

    def __str__(self):
        return self.nom


class Centre(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='centre_logos/', null=True, blank=True)
    cygle = models.CharField(max_length=100, null=True, blank=True)
    adresse = models.TextField()

    def __str__(self):
        return self.nom


class ArtisteInvite(models.Model):
    nom = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    image_artiste = models.ImageField(upload_to='artiste_invite_images/', null=True, blank=True)

    def __str__(self):
        return self.nom


class CategorieArtiste(models.Model):
    CATEGORIE_CHOICES = [
        ('nationale', 'Nationale'),
        ('internationale', 'Internationale'),
    ]
    nom_artiste = models.ForeignKey(ArtisteInvite, on_delete=models.CASCADE, related_name='categories')
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)

    def __str__(self):
        return self.nom_artiste.nom


class TypeDiffusion(models.Model):
    nom = models.CharField(max_length=100)
    is_gratuit = models.BooleanField(default=False)

    def __str__(self):
        return self.nom
    
    
class TypeSpectacle(models.Model):
    type = models.CharField(max_length=100)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return self.type


class Spectacle(models.Model):
    type_spectacle = models.ForeignKey(TypeSpectacle, on_delete=models.CASCADE)
    nom_spectacle = models.CharField(max_length=100)
    image = models.ImageField(upload_to='spectacles/', null=True, blank=True)
    date = models.DateField()
    lieu = models.CharField(max_length=255)
    description = models.TextField()
    ticket_disponible = models.PositiveIntegerField()
    is_gratuit = models.BooleanField(default=False)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    lien_streaming = models.URLField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    

    def __str__(self):
        return f"Spectacle {self.pk}"
    
    
    def generer_code_qr(self):
        if not self.is_gratuit:
            # Construire les données à encoder dans le code QR
            donnees = f"ID: {self.pk}\nNom: {self.nom_spectacle}\nDate: {self.date}\nLieu: {self.lieu}"

            # Générer le code QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(donnees)
            qr.make(fit=True)

            # Créer une image à partir du code QR
            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir l'image en un fichier image
            buffer = BytesIO()
            img.save(buffer)
            nom_fichier = f"code_qr_{slugify(self.nom_spectacle)}_{self.pk}.png"
            fichier_image = File(buffer, name=nom_fichier)

            # Sauvegarder le fichier image dans le champ code_qr du modèle CodeQR
            code_qr = CodeQR.objects.create(spectacle=self)
            code_qr.code_qr.save(nom_fichier, fichier_image)

            # Générer un token sécurisé
            code_qr.generer_token()
            # Générer un code secret
            code_qr.generer_code_secret()

            return code_qr


@receiver(pre_save, sender=Spectacle)
def update_price(sender, instance, **kwargs):
    if instance.is_gratuit:
        instance.prix = None


class CodeQR(models.Model):
    spectacle = models.OneToOneField(Spectacle, on_delete=models.CASCADE, related_name='code_qr')
    code_qr = models.ImageField(upload_to='codes_qr/', null=True, blank=True)
    token = models.CharField(max_length=32, unique=True)
    code_secret = models.CharField(max_length=6, unique=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Code QR pour {self.spectacle}"

    def generer_token(self):
        if not self.spectacle.is_gratuit:
            # Générer un token unique composé de caractères alphanumériques
            alphabet = string.ascii_letters + string.digits
            token = ''.join(secrets.choice(alphabet) for _ in range(32))

            # Vérifier si le token est déjà utilisé
            while CodeQR.objects.filter(token=token).exists():
                token = ''.join(secrets.choice(alphabet) for _ in range(32))

            self.token = token
            self.save()
    
    def generer_code_secret(self):
        # Logique pour générer un code secret à 6 chiffres
        characters = string.ascii_uppercase + string.digits
        self.code_secret = ''.join(random.choice(characters) for _ in range(6))
        self.save()


class Achat(models.Model):
    spectacle = models.ForeignKey(Spectacle, on_delete=models.CASCADE)
    user_email = models.EmailField()
    quantity = models.PositiveIntegerField()
    date_achat = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True)
    statut_paiement = models.CharField(max_length=20)

    def __str__(self):
        return f"Achat {self.transaction_id} pour {self.spectacle}"



class ProchainConcert(models.Model):
    date = models.DateTimeField()
    spectacle = models.ForeignKey(Spectacle, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Prochain Concert {self.date} - {self.spectacle.nom_spectacle} - {self.spectacle.id}"

    class Meta:
        ordering = ['date']


    
 
class Reservation(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    spectacle = models.ForeignKey(Spectacle, on_delete=models.CASCADE)
    nombre_billets = models.PositiveIntegerField()
    cout_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut_paiement = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Réservation de {self.nom} pour {self.spectacle}"


class TypeInstrument(models.Model):
    type_instrument = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type_instrument

    
class Instrument(models.Model):
    type_instrument = models.ForeignKey(TypeInstrument, on_delete=models.CASCADE) 
    nom_instructeur = models.CharField(max_length=100)
    prenom_instructeur = models.CharField(max_length=100)
    

    def __str__(self):
        return f"{self.type_instrument}"
    

class NomFormation(models.Model):
    nom_formation = models.CharField(max_length=100, unique=True)
    type_instrument = models.ForeignKey(TypeInstrument, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='instrument/', null=True, blank=True)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.nom_formation}- {self.type_instrument}"
    
    

class Service(models.Model):
    TYPE_FORMATION_CHOICES = [
        ('presentiel', 'Présentiel'),
        ('en_ligne', 'En ligne'),
        ('hybride', 'Hybride'),
    ]
    nom_formation = models.ForeignKey(NomFormation, on_delete=models.CASCADE) 
    type_formation = models.CharField(max_length=20, choices=TYPE_FORMATION_CHOICES)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date_formation = models.DateField()

    def __str__(self):
        return self.nom_formation
    
    
class TypePaiement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class ReserverService(models.Model):
    type_paiement = models.ForeignKey(TypePaiement, on_delete=models.CASCADE)  
    nom_formation = models.ForeignKey(NomFormation, on_delete=models.CASCADE)  
    type_instrument = models.ForeignKey(TypeInstrument, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    telephone = models.CharField(max_length=100)                                                                                                         
    nombre_place = models.PositiveIntegerField()
    date_paiement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Paiement pour {self.nom_formation} - {self.date_paiement}"
    
    
class Restauration(models.Model):
    menu = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='restaurants/')  
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom
    

class ComanderMenu(models.Model):
    type_paiement = models.ForeignKey(TypePaiement, on_delete=models.CASCADE)   
    menu = models.ForeignKey(Restauration, on_delete=models.CASCADE) 
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    telephone = models.CharField(max_length=100)                                                                                                         
    nombre_commande = models.PositiveIntegerField()
    date_paiement = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    is_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"Paiement pour {self.menu} - {self.date_paiement}"


class Payment(models.Model):
    date = models.DateTimeField(default=timezone.now)
    montant = models.DecimalField(max_digits=10, decimal_places=3, blank=True)
    montant_remis = models.DecimalField(max_digits=10, decimal_places=3, blank=True)
    relicat = models.DecimalField(max_digits=10, decimal_places=3, blank=True)


class ReserverFormation(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    nombre_de_places = models.PositiveIntegerField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Réservation de {self.nom} {self.prenom} pour {self.instrument}"
