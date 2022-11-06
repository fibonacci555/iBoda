from multiprocessing import context
from django.shortcuts import render
from django.views import View
from social.models import Post
from django.shortcuts import render, redirect
from django.db.models import Q 
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.models import User
from django.utils import timezone
import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import render 


class Index(View):
    def get(self, request, *args, **kwargs):

        all_posts = Post.objects.all()
        
        context = {
            'post_list':all_posts,
        }

        date = self.request.GET.get('date')
        
        city = self.request.GET.get('city')
        
        words = self.request.GET.get('words')
       
        


        

        return render(request, 'landing/index.html',context)
