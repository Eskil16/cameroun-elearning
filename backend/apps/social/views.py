from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Follow, FeedItem, Like
from .serializers import FeedItemSerializer, FollowSerializer
from apps.users.serializers import UserPublicSerializer
from apps.users.utils import api_response

User = get_user_model()


def get_lang(request):
    if request.user.is_authenticated:
        return request.user.preferred_language
    return 'fr'


class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        lang = get_lang(request)
        if request.user.pk == pk:
            return api_response(
                message_fr='Vous ne pouvez pas vous suivre vous-même.',
                message_en='You cannot follow yourself.',
                success=False, status_code=status.HTTP_400_BAD_REQUEST, lang=lang,
            )
        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return api_response(
                message_fr='Utilisateur introuvable.',
                message_en='User not found.',
                success=False, status_code=status.HTTP_404_NOT_FOUND, lang=lang,
            )
        _, created = Follow.objects.get_or_create(follower=request.user, following=target)
        return api_response(
            message_fr=f'Vous suivez maintenant {target.get_full_name()}.' if created else 'Déjà abonné.',
            message_en=f'You are now following {target.get_full_name()}.' if created else 'Already following.',
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            lang=lang,
        )


class UnfollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        lang = get_lang(request)
        Follow.objects.filter(follower=request.user, following_id=pk).delete()
        return api_response(
            message_fr='Vous ne suivez plus cet utilisateur.',
            message_en='You are no longer following this user.',
            lang=lang,
        )


class FollowersListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.filter(following_set__following_id=self.kwargs['pk'])


class FollowingListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.filter(followers_set__follower_id=self.kwargs['pk'])


class FeedView(generics.ListAPIView):
    serializer_class = FeedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = user.following_set.values_list('following_id', flat=True)
        return FeedItem.objects.filter(
            Q(actor_id__in=following_ids) | Q(actor=user)
        ).select_related('actor', 'course', 'badge').order_by('-created_at')


class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        lang = get_lang(request)
        try:
            item = FeedItem.objects.get(pk=pk)
        except FeedItem.DoesNotExist:
            return api_response(
                message_fr='Publication introuvable.',
                message_en='Post not found.',
                success=False, status_code=status.HTTP_404_NOT_FOUND, lang=lang,
            )
        like, created = Like.objects.get_or_create(user=request.user, feed_item=item)
        if created:
            item.likes_count += 1
            item.save(update_fields=['likes_count'])
            # Réputation pour l'auteur
            from apps.reputation.services import grant_reputation
            grant_reputation(item.actor, 'like_received',
                             description_fr='Like reçu sur une publication',
                             description_en='Like received on a post')
        else:
            like.delete()
            item.likes_count = max(0, item.likes_count - 1)
            item.save(update_fields=['likes_count'])
        return api_response(
            message_fr='Like ajouté.' if created else 'Like retiré.',
            message_en='Liked.' if created else 'Unliked.',
            lang=lang,
        )
