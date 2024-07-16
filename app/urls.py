from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from . import views
from administration.views import *
from django.conf.urls.i18n import set_language
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

# from django.contrib.auth import views as auth_views
# from .views import HomeView
# from django.contrib.auth.views import LogoutView

urlpatterns = [
    
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
	path('register/', RegisterUserView.as_view(), name='register'),
	
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),
    path('api/delete-user/<int:user_id>/', delete_user, name='delete_user'),

	path('login/', login_view, name='login'),
	path('reset_password_email/', reset_password_email, name='reset_password_email'),
	path('reset_password_confirm/<str:uidb64>/<str:token>', reset_password_confirm, name='reset_password_confirm'),
 
    # path('assign_artiste_profile/', RendreArtisteView.as_view(), name='assign_artiste_profile'),
    path('artistes/', ArtistesListView.as_view(), name='artistes-list'),
    
    path('centre/', CentreViewSet.as_view({'get': 'list', 'post': 'create'}), name='centre'),
    path('centre/<int:pk>/', CentreViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='centre-detail'),
    
    path('artiste_invite/', ArtisteInviteViewSet.as_view({'get': 'list', 'post': 'create'}), name='artiste_invite'),
    path('artiste_invite/<int:pk>/', ArtisteInviteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='artiste-invite-detail'),
    
    path('categorie_artiste/', CategorieArtisteViewSet.as_view({'get': 'list', 'post': 'create'}), name='categorie_artiste'),
    path('categorie_artiste/<int:pk>/', CategorieArtisteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='categorie-artiste-detail'),
    
    path('type_diffusion/', TypeDiffusionViewSet.as_view({'get': 'list', 'post': 'create'}), name='type_diffusion'),
    path('type_diffusion/<int:pk>/', TypeDiffusionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='type-diffusion-detail'),
    
    path('type_spectacle/', TypeSpectacleViewSet.as_view({'get': 'list', 'post': 'create'}), name='type_spectacle'),
    path('type_spectacle/<int:pk>/', TypeSpectacleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='type-spectacle-detail'),
    
    path('spectacle/', SpectacleViewSet.as_view({'get': 'list', 'post': 'create'}), name='spectacle'),
    path('spectacle/<int:pk>/', SpectacleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='spectacle-detail'),
    path('regenerate-qr-codes/', views.regenerate_qr_codes, name='regenerate_qr_codes'),
    
    path('codeqr/', views.CodeQRListCreateAPIView.as_view(), name='codeqr-list-create'),
    path('codeqr/<int:pk>/', views.CodeQRRetrieveUpdateDestroyAPIView.as_view(), name='codeqr-retrieve-update-destroy'),
    
    path('reservation/', ReservationViewSet.as_view({'get': 'list', 'post': 'create'}), name='reservation'),
    path('reservation/<int:pk>/', ReservationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='reservation-detail'),
    
    path('type_instrument/', TypeInstrumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='type_instrument'),
    path('type_instrument/<int:pk>/', TypeInstrumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='type-instrument-detail'),
    
    path('instrument/', InstrumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='instrument'),
    path('instrument/<int:pk>/', InstrumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='instrument-detail'),
    
    path('nom_formation/', NomFormationViewSet.as_view({'get': 'list', 'post': 'create'}), name='nom_formation'),
    path('nom_formation/<int:pk>/', NomFormationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='nom-formation-detail'),
    
    path('reserver_formation/', ReserverFormationViewSet.as_view({'get': 'list', 'post': 'create'}), name='reserver_formation'),
    path('reserver_formation/<int:pk>/', ReserverFormationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='reserver-formation-detail'),
    
    path('services/', ServiceViewSet.as_view({'get': 'list', 'post': 'create'}), name='services'),
    path('services/<int:pk>/', ServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='services-detail'),
    
    path('type_paiement/', TypePaiementViewSet.as_view({'get': 'list', 'post': 'create'}), name='type_paiement'),
    path('type_paiement/<int:pk>/', TypePaiementViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='type-paiement-detail'),
    
    path('reservation_services/', ReserverServiceViewSet.as_view({'get': 'list', 'post': 'create'}), name='reservation_services'),
    path('reservation_services/<int:pk>/', ReserverServiceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='reservation-services-detail'),
    
    path('restauration/', RestaurationViewSet.as_view({'get': 'list', 'post': 'create'}), name='restauration'),
    path('restauration/<int:pk>/', RestaurationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='restauration-detail'),
    
    path('commander_menue/', ComanderMenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='commander_menue'),
    path('commander_menue/<int:pk>/', ComanderMenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='commander-menue-detail'),
    
    path('payment', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment'),
    path('payment/<int:pk>/', PaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='payment-detail'),
    
    
###################    La vue des pages    ###################
    
    path('home', home, name='home'),
    path('streamings/', streamings, name='streamings'),
    path('access_streaming/<int:spectacle_id>/', views.access_streaming, name='access_streaming'),
    path('webhook/kkiapay/', views.kkiapay_webhook, name='kkiapay_webhook'),
    path('shows/', ShowsListView.as_view(), name='shows'),
    path('shows/<int:type_spectacle_id>/', ShowsListView.as_view(), name='shows_by_type'),
    path('service/', service, name='service'), 
    path('ticketdetails/<int:spectacle_id>/', ticketdetails, name='ticketdetails'),
    path('restaurant/', restaurant, name='restaurant'),
    path('reservet/', reservet, name='reservet'), 
    path('commander/', commander, name='commander'),
    
    
    path('change_language/<str:language>/', views.change_language, name='change_language'),
    
    path('page_register/', page_register, name='page_register'),
    path('page_login/', page_login, name='page_login'),
    path('logout/', LogoutView.as_view(next_page=('home')), name='logout'),
    path('page_password_email/', page_password_email, name='page_password_email'),
    
  
   
]



