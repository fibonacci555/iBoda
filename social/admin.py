from django.contrib import admin
from .models import Post ,UserProfile, Comment, Product

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Product)
#admin.site.register(Notification)


