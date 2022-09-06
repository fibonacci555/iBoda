from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views import View
from .models import Post, Comment, UserProfile
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.models import User
from django.utils import timezone











class PostListView(View):
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
            

        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddReport(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        print((post.reports.all()))
        print(post.approved)
        if len(post.reports.all())>=25:
            post.approved=False
            post.save()
        
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



class AllSearch(View):
    def get(self,request,*args,**kwargs):
        date = self.request.GET.get('date')
        
        city = self.request.GET.get('city')
        
        words = self.request.GET.get('words')
        user = False
        

        if date != "" and city != "" and words != "" :
            post_list = Post.objects.filter(Q(date=date) and Q(city__icontains=city) and Q(title__icontains=words) and Q(body__icontains=words)).order_by('-created_on')

        if date == "" and city != "" and words == "":
            post_list = Post.objects.filter(Q(city__icontains=city)).order_by('-created_on')

        if date == "" and city != "" and words != "":
            post_list = Post.objects.filter(Q(city__icontains=city) and Q(title__icontains=words) and Q(body__icontains=words)).order_by('-created_on')

        if date == "" and city == "" and words != "":
            post_list = Post.objects.filter( Q(title__icontains=words) and Q(body__icontains=words)).order_by('-created_on')

        if date != "" and city == "" and words == "":
            post_list = Post.objects.filter(Q(date=date)).order_by('-created_on')

        if date != "" and city != "" and words == "" :
            post_list = Post.objects.filter(Q(date=date) and Q(city__icontains=city) ).order_by('-created_on')

        if date != "" and city == "" and words != "" :
            post_list = Post.objects.filter(Q(date=date) and (Q(title__icontains=words) and Q(body__icontains=words)) ).order_by('-created_on')


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


class ListSavedPosts(LoginRequiredMixin, View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        posts = Post.objects.all().order_by('-created_on')




        context = {
            'post_list' : posts,
        }
        
        return render(request, 'social/saved_posts.html' , context)

class ListLikedPosts(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        posts = Post.objects.all().order_by('-created_on')




        context = {
            'post_list' : posts,
        }
        
        return render(request, 'social/liked_posts.html' , context)


class AddSave(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
 

        is_saved = False

        for save in post.saves.all():
            if save == request.user:
                is_saved = True
                break

        if not is_saved:
            post.saves.add(request.user)
            

        if is_saved:
            post.saves.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddFav(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
 
        print(post.favs.all())
        is_fav = False

        for fav in post.favs.all():
            if fav == request.user:
                is_fav = True
                break

        if not is_fav:
            post.favs.add(request.user)
            

        if is_fav:
            post.favs.remove(request.user)



        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class ListFavPosts(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        posts = Post.objects.all().order_by('-created_on')




        context = {
            'post_list' : posts,
        }
        
        return render(request, 'social/fav_posts.html' , context)


        



