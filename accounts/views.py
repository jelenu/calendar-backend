from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, ValidationError
from rest_framework.throttling import AnonRateThrottle
import logging
from datetime import datetime
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Configure logger
logger = logging.getLogger("password_reset")
handler = logging.FileHandler("password_reset.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

@extend_schema(tags=["Token Management"])
class TokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=["Token Management"])
class TokenRefreshView(TokenRefreshView):
    pass

@extend_schema(tags=["Registration"], request=RegisterSerializer)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{get_current_site(request).domain}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"

            send_mail(
                subject='Activate your account',
                message=f'Actuvate your account using this link: {activation_link}',
                from_email='noreply@authsystem.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({'msg': 'User created. Please check your email to activate your account.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Registration"])
class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(CustomUser, pk=uid)
        except (TypeError, ValueError, OverflowError):
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({'error': 'Account already active.'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'msg': 'Account actived'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Example Protected View"])
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'msg': f'{request.user.email}, you have access to this protected view.'}, status=status.HTTP_200_OK)



User = get_user_model()

class PasswordResetRequestThrottle(AnonRateThrottle):
    rate = '6/hour'
@extend_schema(
    tags=["Password Reset"],
    request=PasswordResetRequestSerializer,
)
class PasswordResetRequestView(APIView):
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"Password reset requested for {email} from IP {ip} at {datetime.now()}")
        if not user:
            return Response({'msg': 'This email does not exist in our system.'}, status=status.HTTP_404_NOT_FOUND)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"http://{get_current_site(request).domain}/api/auth/reset-password-confirm/{uid}/{token}/"

        send_mail(
            subject='Reset your password',
            message=f'Use this link to reset your password: {reset_url}',
            from_email='noreply@authsystem.com',
            recipient_list=[email],
        )
        return Response({'msg': 'If the email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)

@extend_schema(
    tags=["Password Reset"],
    request=PasswordResetConfirmSerializer,
)
class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        password = serializer.validated_data["password"]
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        try:
            validate_password(password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=400)

        user.set_password(password)
        user.save()
        ip = request.META.get('REMOTE_ADDR')
        logger.info(f"Password reset confirmed for {user.email} from IP {ip} at {datetime.now()}")
        return Response({"msg": "Password reset successfully"}, status=200)
    
from rest_framework.permissions import IsAuthenticated

@extend_schema(
    tags=["Password Change"],
    request=PasswordChangeSerializer,
)
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        user = request.user

        if not old_password or not new_password:
            return Response({"error": "Both old_password and new_password are required."}, status=400)

        if not user.check_password(old_password):
            return Response({"error": "Incorrect current password"}, status=400)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"msg": "Password changed successfully"}, status=200)
