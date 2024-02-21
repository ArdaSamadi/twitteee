from django.shortcuts import render

# Create your views here.
# views.py in the 'tweets' app
from rest_framework import generics
from .models import Tweet, Comment
from .serializers import TweetSerializer, CommentSerializer, TweetCreationSerializer
from .models import Follow
from .serializers import FollowSerializer, LikeSerializer, RetweetSerializer, UserCreationSerializer
from .models import UserProfile  , Retweet, Like
from .serializers import UserProfileSerializer , ProfileSerializer, FollowRequestListSerializer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .permissions import IsOwnerOrReadOnly, IsFollowOwnerOrReadOnly
from rest_framework import serializers
from django.contrib.auth.models import User

class TweetCreateView(generics.CreateAPIView):
    queryset = Tweet.objects.all()
    serializer_class = TweetCreationSerializer
    permission_classes = [IsAuthenticated]
class TweetListView(generics.ListAPIView):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]
class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated]


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated]

class TweetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = [IsOwnerOrReadOnly,IsAuthenticated]

class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated]

    def get_tweet(self, tweet_id):
        try:
            return Tweet.objects.get(pk=tweet_id)
        except Tweet.DoesNotExist:
            return None

    def perform_create(self, serializer):
        tweet_id = self.kwargs['pk']
        tweet = self.get_tweet(tweet_id)
        ret = True
        if tweet:
            user = self.request.user
            existing_like = tweet.like_set.filter(user=user).first()
            if existing_like:
                existing_like.delete()
                ret = False
            else:
                like = Like(user=user, tweet=tweet)
                like.save()
                ret=False
            return Response({'Liked' : ret})
        else:
            return Response({'detail': 'Tweet not found'}, status=status.HTTP_404_NOT_FOUND)

class RetweetCreateView(generics.CreateAPIView):
    queryset = Retweet.objects.all()
    serializer_class = RetweetSerializer
    permission_classes = [IsAuthenticated]

class FollowListCreateView(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated]

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Tweet.DoesNotExist:
            return None

    def perform_create(self, serializer):
        user_id = self.kwargs['pk']
        following = self.get_user(user_id)
        user = self.request.user
        if (following == user):
            return Response({'detail': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        existing_follow = Follow.objects.all().filter(follower=user,following=following).first()
        ret = True
        if existing_follow:
            existing_follow.delete()
            ret = False
        else:
            follow = Follow(follower=user,following=following,is_accepted=(following.userprofile.is_public==True))
            follow.save()
            ret=False
        return Response({'Followed' : ret})
        
    


class UserTweetsListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.kwargs['user']
        return Tweet.objects.filter(user=user)

class FollowingTweetsListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = [follow.following for follow in Follow.objects.filter(follower=user)]
        return (Tweet.objects.filter(user__in=following_users)) | (Tweet.objects.filter(user=user))

class RecommendedTweetsListView(generics.ListAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the user making the request
        user = self.request.user

        # Get liked tweet content for the user
        user_liked_tweets = Like.objects.filter(user=user).values_list('tweet__content', flat=True)

        if not user_liked_tweets:
            # Handle the case where the user has no liked tweets
            return Tweet.objects.none()

        # Get liked tweet content for all other users
        all_users_liked_tweets = [
            Like.objects.filter(user=u).values_list('tweet__content', flat=True) for u in User.objects.exclude(id=user.id)
        ]

        # Filter out empty liked tweet content
        all_users_liked_tweets = [tweets for tweets in all_users_liked_tweets if tweets]

        if not all_users_liked_tweets:
            # Handle the case where there are no liked tweets from other users
            return Tweet.objects.none()

        # Create a TF-IDF vectorizer
        vectorizer = TfidfVectorizer()

        try:
            # Fit and transform the vectorizer on the user's and other users' tweet content
            user_vector = vectorizer.fit_transform(user_liked_tweets)
            all_users_vectors = [vectorizer.transform(u_liked_tweets) for u_liked_tweets in all_users_liked_tweets]
        except ValueError as e:
            # Handle the case where TF-IDF vectorization fails
            print("TF-IDF Vectorization Error:", e)
            return Tweet.objects.none()

        # Calculate cosine similarity between the user and all other users
        similarities = [cosine_similarity(user_vector, u_vector)[0][0] for u_vector in all_users_vectors]

        # Sort users based on similarity in descending order
        similar_users = sorted(zip(User.objects.exclude(id=user.id), similarities), key=lambda x: x[1], reverse=True)

        if not similar_users:
            # Handle the case where there are no similar users
            return Tweet.objects.none()

        # Get recommended tweets from the most similar user
        most_similar_user, _ = similar_users[0]
        recommended_tweets = Tweet.objects.filter(like__user=most_similar_user)
        # following_users = [follow.following for follow in Follow.objects.filter(follower=user)]
        following_users = [follow.following for follow in Follow.objects.filter(follower=user)]
        return recommended_tweets | (Tweet.objects.filter(user__in=following_users)) | (Tweet.objects.filter(user=user))

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]  # Allow any user to access the login view

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = RefreshToken.for_user(response.data['user'])
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response




def find_similar_users(user):
    # Get the list of users who have interacted with tweets
    users = User.objects.exclude(id=user.id)

    # Get the liked tweet content for the given user
    user_liked_tweets = Like.objects.filter(user=user).values_list('tweet__content', flat=True)

    # Get liked tweet content for all other users
    all_users_liked_tweets = [
        Like.objects.filter(user=u).values_list('tweet__content', flat=True) for u in users
    ]

    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the vectorizer on the user's and other users' tweet content
    user_vector = vectorizer.fit_transform(user_liked_tweets)
    all_users_vectors = [vectorizer.transform(u_liked_tweets) for u_liked_tweets in all_users_liked_tweets]

    # Calculate cosine similarity between the user and all other users
    similarities = [cosine_similarity(user_vector, u_vector)[0][0] for u_vector in all_users_vectors]

    # Sort users based on similarity in descending order
    similar_users = sorted(zip(users, similarities), key=lambda x: x[1], reverse=True)

    # Return a list of similar users
    return [user for user, _ in similar_users]

# tweets/views.py



class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreationSerializer  # Replace with your custom serializer for registration

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile
    
class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size = 10  # Adjust the page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 100

class FollowRequestListView(generics.ListAPIView):
    serializer_class = FollowRequestListSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        user = self.request.user
        follow_requests = Follow.objects.filter(following=user, is_accepted=False)
        return follow_requests
    
class AcceptFollowRequestView(generics.UpdateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated,IsFollowOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_accepted = True
        instance.save()
        return Response({'detail': 'Follow request accepted successfully.'}, status=status.HTTP_200_OK)

class DenyFollowRequestView(generics.DestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated,IsFollowOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'detail': 'Follow request denied successfully.'}, status=status.HTTP_204_NO_CONTENT)
