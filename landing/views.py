from multiprocessing import context
from django.shortcuts import render
from django.views import View

from social.models import Post 


class Index(View):
    def get(self, request, *args, **kwargs):

        all_posts = Post.objects.all()

        context = {
            'post_list':all_posts,
        }


        return render(request, 'landing/index.html',context)
