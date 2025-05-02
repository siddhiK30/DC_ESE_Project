# from django.urls import path
# from django.contrib import admin
# from .views import (
#     SignupView, 
#     LoginView, 
#     HomeView, 
#     GuestbookListView,
#     CreateGuestbookEntryView,
#     DeleteGuestbookEntryView
# )

# # Define URL patterns for both API and browser access
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', LoginView.as_view(), name='login'),
#     path('signup/', SignupView.as_view(), name='signup'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('home/', HomeView.as_view(), name='home'),
#     path('guestbook/', GuestbookListView.as_view(), name='guestbook_home'),
#     path('guestbook/create/', CreateGuestbookEntryView.as_view(), name='create_entry'),
#     path('guestbook/delete/<int:entry_id>/', DeleteGuestbookEntryView.as_view(), name='delete_guestbook_entry'),
    
#     # API endpoints
#     path('api/signup/', SignupView.as_view(), name='api_signup'),
#     path('api/login/', LoginView.as_view(), name='api_login'),
#     path('api/home/', HomeView.as_view(), name='api_home'),
#     path('api/guestbook/', GuestbookListView.as_view(), name='api_guestbook_home'),
#     path('api/guestbook/create/', CreateGuestbookEntryView.as_view(), name='api_create_entry'),
#     path('api/guestbook/delete/<int:entry_id>/', DeleteGuestbookEntryView.as_view(), name='api_delete_guestbook_entry'),
# ]
from django.urls import path
from django.contrib import admin
from .views import (
    SignupView, 
    LoginView, 
    HomeView, 
    GuestbookListView,
    CreateGuestbookEntryView,
    DeleteGuestbookEntryView,
    RPCView
)

# Define URL patterns for both API and browser access
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('guestbook/', GuestbookListView.as_view(), name='guestbook_home'),
    path('guestbook/create/', CreateGuestbookEntryView.as_view(), name='create_entry'),
    path('guestbook/delete/<int:entry_id>/', DeleteGuestbookEntryView.as_view(), name='delete_guestbook_entry'),
    
    # API endpoints
    path('api/signup/', SignupView.as_view(), name='api_signup'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/home/', HomeView.as_view(), name='api_home'),
    path('api/guestbook/', GuestbookListView.as_view(), name='api_guestbook_home'),
    path('api/guestbook/create/', CreateGuestbookEntryView.as_view(), name='api_create_entry'),
    path('api/guestbook/delete/<int:entry_id>/', DeleteGuestbookEntryView.as_view(), name='api_delete_guestbook_entry'),
    
    # New RPC endpoints
    path('api/rpc/', RPCView.as_view(), name='api_rpc'),
]