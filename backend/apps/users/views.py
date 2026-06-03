from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings as django_settings

from .serializers import (
    RegisterSerializer, UserPublicSerializer, UserMeSerializer,
    ChangePasswordSerializer, UserUpdateSerializer,
)
from .utils import generate_verification_code, api_response

User = get_user_model()


def get_lang(request):
    if request.user.is_authenticated:
        return request.user.preferred_language
    return request.headers.get('Accept-Language', 'fr')[:2]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        code = generate_verification_code()
        user.verification_code = code
        user.save(update_fields=['verification_code'])

        # Envoi du code par email
        try:
            send_mail(
                subject='Code de vérification — Réseau Académique Camerounais',
                message=f'Votre code de vérification est : {code}',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        refresh = RefreshToken.for_user(user)
        return api_response(
            data={
                'user': UserMeSerializer(user, context={'request': request}).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
            },
            message_fr='Compte créé avec succès. Vérifiez votre email.',
            message_en='Account created. Check your email for the verification code.',
            status_code=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '')
        lang = get_lang(request)
        if code and code == request.user.verification_code:
            request.user.is_verified = True
            request.user.verification_code = ''
            request.user.save(update_fields=['is_verified', 'verification_code'])
            return api_response(
                message_fr='Email vérifié avec succès.',
                message_en='Email verified successfully.',
                lang=lang,
            )
        return api_response(
            message_fr='Code invalide ou expiré.',
            message_en='Invalid or expired code.',
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            lang=lang,
        )


class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserMeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        lang = get_lang(request)
        return api_response(
            data=UserMeSerializer(instance, context={'request': request}).data,
            message_fr='Profil mis à jour.',
            message_en='Profile updated.',
            lang=lang,
        )


class UserPublicProfileView(generics.RetrieveAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return api_response(data=serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lang = get_lang(request)
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return api_response(
                message_fr='Mot de passe actuel incorrect.',
                message_en='Current password is incorrect.',
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
                lang=lang,
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return api_response(
            message_fr='Mot de passe modifié avec succès.',
            message_en='Password changed successfully.',
            lang=lang,
        )
