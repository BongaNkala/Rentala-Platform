from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.models import User, PlatformSession
import uuid

class LoginView(views.APIView):
    """Multi-platform login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        platform = request.data.get('platform', 'web')
        device_id = request.data.get('device_id', '')
        device_name = request.data.get('device_name', '')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            # Create platform session
            session = PlatformSession.objects.create(
                user=user,
                platform=platform,
                device_id=device_id,
                device_name=device_name,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=self.get_client_ip(request)
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Update user's last platform
            user.last_platform = platform
            user.save(update_fields=['last_platform'])
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': str(user.uuid),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_host': user.is_host,
                    'avatar': user.avatar.url if user.avatar else None,
                },
                'session_id': str(session.session_id),
                'platform': platform
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(views.APIView):
    """Multi-platform logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        session_id = request.data.get('session_id')
        
        if session_id:
            try:
                session = PlatformSession.objects.get(
                    session_id=session_id,
                    user=request.user
                )
                session.is_active = False
                session.logged_out_at = timezone.now()
                session.save()
            except PlatformSession.DoesNotExist:
                pass
        
        return Response({'message': 'Successfully logged out'})


class RegisterView(views.APIView):
    """Multi-platform registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Registration logic here
        pass
