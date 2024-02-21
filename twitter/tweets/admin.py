from django.contrib import admin
from .models import Tweet, Comment, UserProfile, Retweet, Follow, Like
# Register your models here.
admin.site.register(Tweet)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Retweet)
admin.site.register(Follow)
admin.site.register(Like)