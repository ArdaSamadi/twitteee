# tweets/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    TweetCreateView,
    CommentListCreateView,
    FollowListCreateView,
    UserProfileDetailView,
    UserTweetsListView,
    FollowingTweetsListView,
    RecommendedTweetsListView,
    LikeCreateView,
    RetweetCreateView,
    RegisterView,
    MyProfileView,
    CustomTokenObtainPairView,
    TweetListView,
    TweetDetailView,
    FollowRequestListView,
    AcceptFollowRequestView,
    DenyFollowRequestView
)

urlpatterns = [
    path('tweets/<int:pk>/', TweetDetailView.as_view(), name='tweet-list-detail'),
    path('tweets/create/', TweetCreateView.as_view(), name='tweet-list-create'),
    path('comments/<int:pk>/', CommentListCreateView.as_view(), name='comment-detail'),
    path('like/<int:pk>/', LikeCreateView.as_view(), name='like-create'),
    path('follow/<int:pk>/', FollowListCreateView.as_view(), name='follow-list-create'),
    #follows have problem
    path('user-profile/<int:pk>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
    path('user-tweets/<int:user>/', UserTweetsListView.as_view(), name='user-tweets-list'),
    path('tweets/', FollowingTweetsListView.as_view(), name='tweets-list'),
    path('recommended-tweets/', RecommendedTweetsListView.as_view(), name='recommended-tweets-list'),
    path('retweet/', RetweetCreateView.as_view(), name='retweet-create'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my-profile/', MyProfileView.as_view(), name='my-profile'),
    path('requests/', FollowRequestListView.as_view(), name='requests'),
    path('requests/<int:pk>/accept/', AcceptFollowRequestView.as_view(), name='accept-follow-request'),
    path('requests/<int:pk>/deny/', DenyFollowRequestView.as_view(), name='deny-follow-request'),

]   

