from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import GuestbookEntry
from .serializers import GuestbookEntrySerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password

class SignupView(APIView):
    def get(self, request):
        """Render signup form for browser requests"""
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, "signup.html")  # Ensure you create this template
        return Response({"message": "Use POST to sign up"}, status=status.HTTP_200_OK)

    def post(self, request):
        """Handle signup form submission"""
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        user = User.objects.create(username=username, email=email, password=make_password(password))

        # Redirect to login page after signup success
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, "login.html", {"message": "Account created successfully! Please log in."})

        return Response({"message": "Account created successfully!"}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def get(self, request):
        """Return HTML for browser access"""
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, "login.html")  
        return Response({"message": "Use POST to log in"}, status=status.HTTP_200_OK)

    def post(self, request):
        """Return JSON for API access"""
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return redirect('home')  # Redirect to home page after login
            return Response({"message": "Login successful", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return HTML for browser access, JSON for API requests"""
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, "home.html")  
        return Response({"message": "Welcome to the Home Page!"}, status=status.HTTP_200_OK)

class GuestbookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = GuestbookEntry.objects.filter(recipients=request.user)
        serializer = GuestbookEntrySerializer(entries, many=True)

        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return render(request, "guestbook/guestbook_home.html", {"entries": serializer.data})

        return Response(serializer.data, status=status.HTTP_200_OK)

from .models import GuestbookEntry

class DeleteGuestbookEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, entry_id):
        entry = get_object_or_404(GuestbookEntry, id=entry_id)

        if request.user in entry.recipients.all():
            entry.recipients.remove(request.user)
            if entry.recipients.count() == 0:
                entry.delete()
            
            # Check if it's a browser request
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return redirect('guestbook_home')
            
            # Return JSON response for API requests
            return Response({"message": "Entry deleted"}, status=status.HTTP_204_NO_CONTENT)

        # Handle unauthorized access
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            return redirect('guestbook_home')  # Redirect even on error for better UX
        return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, entry_id):
        """Handle POST requests for form submissions that can't use DELETE method"""
        return self.delete(request, entry_id)

class CreateGuestbookEntryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Renders the HTML page with a list of users"""
        users = User.objects.exclude(id=request.user.id)  # Get all users except the logged-in user
        return render(request, 'guestbook/create_entry.html', {"users": users})

    def post(self, request):
        """Handles form submission to create a guestbook entry"""
        content = request.POST.get('content')  # Get the message content
        recipient_ids = request.POST.get('selectedUsers')  # Comma-separated user IDs

        if not content or not recipient_ids:
            error_message = "Content and recipients are required"
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, 'guestbook/create_entry.html', {
                    "error": error_message,
                    "users": User.objects.exclude(id=request.user.id)
                })
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        recipient_ids = recipient_ids.split(",")  # Convert CSV string into a list
        recipients = User.objects.filter(id__in=recipient_ids)  # Fetch user objects

        if not recipients.exists():
            error_message = "Invalid recipients"
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, 'guestbook/create_entry.html', {
                    "error": error_message,
                    "users": User.objects.exclude(id=request.user.id)
                })
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Create the guestbook entry
        entry = GuestbookEntry.objects.create(sender=request.user, content=content)
        entry.recipients.set(recipients)  # Assign recipients

        # Handle response based on request type
        if "text/html" in request.META.get("HTTP_ACCEPT", ""):
            # Redirect to guestbook home page for HTML requests
            return redirect('guestbook_home')
            
        # Return JSON response for API requests
        return Response({"message": "Guestbook entry created successfully!"}, status=status.HTTP_201_CREATED)