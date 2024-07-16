from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
    
        
User = get_user_model()



class UserAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'email_or_phone', 'last_login_date' ,'last_modify_date', 'deactivate_date', 'first_name', 'last_name', 'is_artistes', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    list_editable = ('first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email_or_phone', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_admin', 'is_artistes', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email_or_phone', 'password1', 'password2')
        }),
    )

    search_fields = ('email_or_phone',)
    ordering = ('id',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)



@admin.register(Artistes)
class ArtistesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'biographie', 'image')  
    ordering = ('id',)


@admin.register(Centre)
class CentreAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'logo', 'cygle', 'adresse')
    ordering = ('id',)


@admin.register(TypeDiffusion)
class TypeDiffusionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'is_gratuit')
    search_fields = ('nom',)
    ordering = ('id',)
    

@admin.register(ArtisteInvite)
class ArtisteInviteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'phone', 'image_artiste')
    search_fields = ('nom', 'phone')
    ordering = ('id',)


@admin.register(CategorieArtiste)
class CategorieArtisteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_artiste', 'categorie')
    search_fields = ('nom_artiste__nom', 'categorie')
    ordering = ('id',)

    
@admin.register(TypeSpectacle)
class TypeSpectacleAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'is_valid')
    search_fields = ('type',)
    ordering = ('id',)
    

@admin.register(Spectacle)
class SpectacleAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_spectacle', 'nom_spectacle', 'image', 'date', 'lieu', 'description', 
                    'ticket_disponible', 'is_gratuit', 'prix', 'heure_debut', 'heure_fin', 'lien_streaming', 'is_valid')
    search_fields = ('nom_spectacle', 'lieu')
    list_filter = ('date', 'is_gratuit')
    ordering = ('id',)


@admin.register(CodeQR)
class CodeQRAdmin(admin.ModelAdmin):
    list_display = ('id', 'spectacle', 'code_qr', 'token', 'device_info', 'is_used')
    search_fields = ('spectacle__nom_spectacle', 'token')
    ordering = ('id',)


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ('id', 'spectacle', 'user_email', 'quantity', 'montant_total', 'date_achat', 'statut_paiement')
    list_filter = ('spectacle', 'statut_paiement', 'date_achat')
    search_fields = ('user_email', 'transaction_id')
    ordering = ('-date_achat',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'email', 'spectacle', 'nombre_billets', 'cout_total', 'statut_paiement', 'is_valid')
    search_fields = ('nom', 'email', 'spectacle__nom_spectacle')
    ordering = ('id',)


@admin.register(TypeInstrument)
class TypeInstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_instrument',)
    search_fields = ('type_instrument',)
    ordering = ('id',)


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_instrument', 'nom_instructeur', 'prenom_instructeur')
    search_fields = ('type_instrument__type_instrument', 'nom_instructeur', 'prenom_instructeur')
    ordering = ('id',)


@admin.register(NomFormation)
class NomFormationAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_formation', 'type_instrument', 'image', 'description', 'prix')
    search_fields = ('nom_formation', 'type_instrument__type_instrument')
    ordering = ('id',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_formation', 'type_formation', 'instrument', 'date_formation')
    search_fields = ('nom_formation__nom_formation', 'type_formation', 'instrument__type_instrument')
    ordering = ('id',)


@admin.register(TypePaiement)
class TypePaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom',)
    search_fields = ('nom',)
    ordering = ('id',)


@admin.register(ReserverService)
class ReserverServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_paiement', 'nom_formation', 'type_instrument', 'nom', 'prenoms', 'telephone', 'nombre_place', 'date_paiement', 'montant', 'is_valid')
    search_fields = ('nom_formation__nom_formation', 'type_instrument__type_instrument', 'nom', 'prenoms', 'telephone')
    ordering = ('id',)


@admin.register(Restauration)
class RestaurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu', 'description', 'image', 'prix')
    search_fields = ('menu',)
    ordering = ('id',)
    

@admin.register(ComanderMenu)
class ComanderMenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_paiement', 'menu', 'nom', 'prenoms', 'telephone', 'nombre_commande', 'date_paiement', 'montant', 'is_valid')
    search_fields = ('menu__menu', 'nom', 'prenoms', 'telephone')
    ordering = ('id',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'montant', 'montant_remis', 'relicat')
    search_fields = ('date',)
    ordering = ('id',)


@admin.register(ReserverFormation)
class ReserverFormationAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'telephone', 'instrument', 'nombre_de_places', 'montant')
    search_fields = ('nom', 'prenom', 'telephone', 'instrument__type_instrument')
    ordering = ('id',)
    

@admin.register(ProchainConcert)
class ProchainConcertAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'spectacle', 'is_active')
    search_fields = ('date',)
    ordering = ('id',)   
    

