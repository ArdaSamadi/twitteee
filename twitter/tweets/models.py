# models.py in the 'tweets' app
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# models.py in the 'tweets' app
class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    retweets = models.ManyToManyField(User, related_name='retweeted_tweets', blank=True)
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # Ensure the combination of follower and following is unique
        unique_together = ['user', 'tweet']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # models.py in the 'tweets' app
class UserProfile(models.Model):
    phone_number_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(validators=[phone_number_regex],max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profile_header = models.ImageField(upload_to='profile_headers/', blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    birth_date = models.DateField(blank=True, null=True)
    is_public = models.BooleanField(default=True, null=False)
# models.py in the 'tweets' app

class Retweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # Ensure the combination of follower and following is unique
        unique_together = ['user', 'tweet']

# models.py in the 'tweets' app
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # Ensure the combination of follower and following is unique
        unique_together = ['follower', 'following']
    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Follower and following cannot be the same.")
        # Call the parent class's clean method
        super().clean()

