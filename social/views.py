from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View
from .models import Post, Comment, UserProfile, Notification
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.models import User
from django.utils import timezone



def is_username(query):
    if "@" in query: 
        return True
    else:
        return False

def is_date(query):
    lista = list(query)
    if len(lista) == 10:
        if lista[0].isnumeric() and lista[1].isnumeric and lista[2] == "-" and lista[3].isnumeric() and lista[4].isnumeric() and lista[5] == "-" and lista[6].isnumeric() and lista[7].isnumeric() and lista[8].isnumeric() and lista[9].isnumeric():
            return True
        else:
            return False
    else:
        return False

def is_local(query):
    if not is_username(query) and not is_date(query):
        return True
    else:
        return False






class PostListView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        all_posts = Post.objects.all()

        posts = all_posts

        if len(posts) != 0: 
            posts = Post.objects.all().order_by('-created_on')

        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
        }
        return render(request, 'social/post_list.html', context)

    def post(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_on')
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

        context = {
            'post_list': posts,
            'form': form,
        }
        return render(request, 'social/post_list.html', context)

class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments' : comments,
        }

        return render(request, 'social/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()

       



        comments = Comment.objects.filter(post=post).order_by('-created_on')
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)

        context = {
            'post': post,
            'form': form,
            'comments' : comments,

        }

        return render(request, 'social/post_detail.html', context)


class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)

        return redirect('post-detail', pk=post_pk)

class PostEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['title', 'city','body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail',kwargs={'pk':pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail',kwargs={'pk':pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author



class ProfileView(View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')
        followers = profile.followers.all()
        n_followers = len(followers)
        is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        #--------------------------------------------
        # fazer função para saber se seguem mutamente
        #--------------------------------------------
        
        context = {
            'user' : user,
            'profile' : profile,
            'posts' : posts,
            'n_followers' : n_followers,
            'is_following' : is_following,
        }

        return render(request, 'social/profile.html', context)


class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','city','picture']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollower(LoginRequiredMixin, View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
        return redirect('profile',pk=profile.pk)

class RemoveFollower(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile',pk=profile.pk)


class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
 

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)

        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddReport(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
 

        is_reported = False

        for report in post.reports.all():
            if report == request.user:
                is_reported = True
                break

        if not is_reported:
            post.reports.add(request.user)
            

        if is_reported:
            post.reports.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

"""class AllSearch(View):
    def get(self,request,*args,**kwargs):
        query = self.request.GET.get('query')
        user = False
        print("user : " , (is_username(query)))
        print("date : " , (is_date(query)))
        print("local : ", (is_local(query)))
        
        if is_username(query):
            new = ""
            for char in query:
                if char == "@":
                    pass
                else:
                    new = new + char
            user = True
            profile_list = UserProfile.objects.filter(
                    Q(user__username__icontains=new)
                ).order_by('-created_on')
            context = {
            'profile_list' : profile_list,
            #'post_list' : post_list,
            'is_user' : user,
            }
            
        elif is_local(query):
            user = False
            post_list = Post.objects.filter(
                    Q(city__icontains=query)
                ).order_by('-created_on')
            post_list_new = post_list.filter(
                    Q(date__icontains=timezone.now)
                ).order_by('-created_on')
            context = {
            #'profile_list' : profile_list,
            'post_list' : post_list,
            'is_user' : user,
            }
        elif is_date(query):
            user = False
            query = query[6]+query[7]+query[8]+query[9]+"-"+query[3]+query[4]+"-"+query[0]+query[1]
            

        

        return render(request, 'social/search.html' , context)"""

class AllSearch(View):
    def get(self,request,*args,**kwargs):
        date = self.request.GET.get('date')
        date = date[6]+date[7]+date[8]+date[9]+"-"+date[3]+date[4]+"-"+date[0]+date[1]
        city = self.request.GET.get('city')
        user = False
        print(date, city)
        post_list = Post.objects.filter(Q(date=date) and Q(city__icontains=city)).order_by('-created_on')
            
        context = {
            'post_list' : post_list,
             'is_user' : user,
        }
        
        return render(request, 'social/search.html' , context)


class ListFollowers(View):
    def get(self,request,pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
        'profile': profile,
        'followers':followers,
        }

        return render(request , 'social/followers_list.html',context)

class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post-detail', pk=post_pk)

class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', pk=profile_pk)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('Success', content_type='text/plain')

        



