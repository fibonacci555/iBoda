from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator



class Post(models.Model):
    title = models.CharField(default="",max_length=70)
    city = models.CharField(default="",max_length=40)
    date = models.DateField(default=timezone.now)
    body = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='uploads/post_photos', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    music = models.CharField(default="",max_length=70)
    url = models.URLField(max_length = 200, blank=True, null=True)
    age = models.CharField(default="",max_length=70)
    approved = models.BooleanField(default=True)
    reports = models.ManyToManyField(User, blank=True, related_name='reports')
    saves = models.ManyToManyField(User, blank=True, related_name='saves')
    favs = models.ManyToManyField(User, blank=True, related_name='favs')
    likes_count = models.PositiveIntegerField(default=0)
    

    
   

    




class Comment(models.Model):
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')

    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-created_on').all()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True,verbose_name='user',related_name='profile',on_delete=models.CASCADE)
    name = models.CharField(max_length = 30, blank=True, null=True)
    verified = models.BooleanField(default=False)
    picture = models.ImageField(upload_to = 'uploads/profile_pictures' ,default='uploads/profile_pictures/default.jpg', blank=True)
    followers = models.ManyToManyField(User,blank=True,related_name='followers')
    public = models.BooleanField(default=True)
    favs_count = models.PositiveIntegerField(default = 0)
    
    def calculate_age(self):
        import datetime
        return int((datetime.datetime.now().date() - self.birthday).days / 365.25  )

    age = property(calculate_age)



    @receiver(post_save, sender=User)
    def create_user_profile(sender,instance,created,**kwargs):
        if created:
            UserProfile.objects.create(user=instance)
        
    @receiver(post_save, sender=User)
    def save_user_profile(sender,instance, **kwargs):
        instance.profile.save()




        
 
    

