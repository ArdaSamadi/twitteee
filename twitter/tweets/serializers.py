# serializers.py in the 'tweets' app
from rest_framework import serializers
from .models import Tweet, Comment,UserProfile ,Comment, Retweet , Follow, Like
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse,reverse_lazy


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_pic']
    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'userprofile'):
            if obj.userprofile.profile_pic:
                return request.build_absolute_uri(obj.userprofile.profile_pic.url)
        return None

class TweetSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    retweets_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = Tweet
        fields = ["id",
        "content",
        "created_at",
        "user",
        "likes_count",
        "retweets_count",
        "comments"
        ]
        read_only_fields = ["user"]
    def get_likes_count(self, obj):
        return obj.like_set.count()
    def get_retweets_count(self, obj):
        return obj.retweets.count()
    def get_comments(self, obj):
        latest_comments = obj.comment_set.order_by('-created_at')[:3]
        return CommentSerializer(latest_comments, many=True).data
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context['request'].user
        is_visible = self.is_tweet_visible(instance, user)
        
        if not is_visible:
            return {}
        return data
    def is_tweet_visible(self, tweet, viewer):
        """
        Determine if the tweet is visible to the given user.
        """
        user_profile = tweet.user.userprofile
        return user_profile.is_public or viewer == tweet.user or (Follow.objects.all().filter(following=tweet.user, follower=viewer,is_accepted=True).exists())
class TweetCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['content']
    def create(self, validated_data):
        user = self.context['request'].user
        tweet = Tweet.objects.create(user=user, **validated_data)
        return tweet
    


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]

# serializers.py in the 'tweets' app
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user','phone_number','bio','profile_pic','profile_header','birth_date','joined_date','is_public']
        read_only_fields = ['user','joined_date']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user','bio','profile_pic','profile_header','birth_date','is_public']
        read_only_fields = ['user','joined_date','bio','profile_pic','profile_header','birth_date','is_public']
    
# serializers.py in the 'tweets' app
# serializers.py in the 'tweets' app
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['tweet']
        read_only_fields = ['tweet']

    def create(self, validated_data):
        user = self.context['request'].user
        
        tweet = get_object_or_404(validated_data['tweet'])
        like = Like.objects.create(user=user, tweet=tweet)
        return like

class RetweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retweet
        fields = ['tweet']
    def create(self, validated_data):
        user = self.context['request'].user
        tweet = Retweet.objects.create(user=user, **validated_data)
        return tweet


# serializers.py in the 'tweets' app
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['following','follower']
        read_only_fields = ['following','follower']
    def create(self, validated_data):
        user = self.context['request'].user
        follow = Follow.objects.create(follower=user, **validated_data)
        return follow


class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        # Validate that the passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Remove confirm_password field before creating the User instance
        validated_data.pop('confirm_password', None)

        # Create the User instance
        user = User.objects.create_user(**validated_data)

        # Create the UserProfile instance associated with the User
        UserProfile.objects.create(user=user)

        return user
    
class FollowRequestListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    follower = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField()

    class Meta:
        fields = ['id', 'follower', 'created_at']