from django.contrib import admin
from .models import Post ,UserProfile, Comment, Product, FollowRequest, Notification

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Notification)
admin.site.register(FollowRequest)


