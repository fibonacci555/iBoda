import pkgutil
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Count, F
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from .models import Post, Comment, UserProfile, Product, FollowRequest, Notification, Feedback
from .forms import PostForm, CommentForm, FeedbackForm
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
from .models import Product
from django.shortcuts import render

stripe.api_key = settings.STRIPE_SECRET_KEY



# type 1 = sender vai ao evento
# type 2 = sender comentou o evento
# type 3 = sender criou um post
# type 4 = sender já não vai ao evento
# type 5 = sender começou a seguir



def page_not_found_view(request,exception):
    return render(request, 'social/404.html', status=404)



class FeedbackView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        


        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')

        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notis = Notification.objects.filter(receiver=request.user)
        notifications = len(notis) + len(frequests)


        form = FeedbackForm()

        context = {
            'form': form,
            'frequests':frequests,
            'notis':notifications,
        }
        return render(request, 'social/feedback.html', context)

    def post(self, request, *args, **kwargs):

        form = FeedbackForm(request.POST)

        if form.is_valid():
                new_post = form.save(commit=False)
                new_post.save()

        context = {
                'form': form,
            }
        return render(request, 'social/feedback.html', context)

class CreatePostView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        


        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')

        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notis = Notification.objects.filter(receiver=request.user)
        notifications = len(notis) + len(frequests)


        form = PostForm()

        context = {
            'form': form,
            'frequests':frequests,
            'notis':notifications,
        }
        return render(request, 'social/create_post.html', context)

    def post(self, request, *args, **kwargs):

        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
                new_post = form.save(commit=False)
                if new_post.public == True:
                    new_post.public = False
                else:
                    new_post.public = True
                new_post.author = request.user
                new_post.save()
        log_user = User.objects.get(username=request.user.username)
        followers = log_user.profile.followers.all()

        for follower in followers:
            new_notification = Notification()
            new_notification.sender = log_user
            new_notification.receiver = follower
            new_notification.type = 3
            new_notification.post = new_post
            new_notification.save()

        


        context = {
                'form': form,
            }
        return render(request, 'social/create_post.html', context)




class PostListView(View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        all_posts = Post.objects.all()
        
        posts = all_posts

        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')

        priv_posts = Post.objects.filter(approved=True,public=False).order_by('-created_on')

        following_users = request.user.profile.following.all()
       
        notis = Notification.objects.filter(receiver=request.user)

        notifications = len(notis) + len(frequests)

        for post in priv_posts:
            
            if post.author not in following_users and request.user != post.author:
                post_id = int(post.id)
                priv_posts = priv_posts.exclude(id=post_id)
                
            else:
                pass
                
            
        
    
        pub_posts = Post.objects.filter(approved=True,public=True).order_by('-created_on')
            
        
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form,
            'frequests':frequests,
            'pub_posts':pub_posts,
            'priv_posts':priv_posts,
            'notis':notifications,
            
        }
        return render(request, 'social/post_list.html', context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')
        notis = Notification.objects.filter(receiver=request.user)
        logged_in_user = request.user
        
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post': post,
            'form': form,
            'comments' : comments,
            'notis':notifications,'frequests':frequests,
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

        log_user = User.objects.get(username=request.user.username)
       

        if request.user != post.author:
            new_notification = Notification()
            new_notification.sender = log_user
            new_notification.receiver = post.author
            new_notification.type = 2
            new_notification.post = post
            new_notification.save()
       



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
        
        log_user = User.objects.get(username=request.user.username)
       
        

        
        new_notification = Notification()
        new_notification.sender = log_user
        new_notification.receiver = post.author
        new_notification.type = 2
        new_notification.post = post
        new_notification.save()

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
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')

        is_requesting = False


        for req in frequests:
            if req.sender == request.user and req.is_active:
                is_requesting = True


        for post in posts:
            
            for user in post.favs.all():

                profile.favs_count = profile.favs_count + 1

        followers = profile.followers.all()

        nfollowing = len(profile.following.all())

        n_followers = len(followers)
        is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        fav_counter = profile.favs_count

        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user

        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'user' : user,
            'profile' : profile,
            'nfollowing':nfollowing,
            'posts' : posts,
            'n_followers' : n_followers,
            'followers' : followers,
            'is_following' : is_following,
            'fav_counter' : fav_counter,
            'is_requesting' : is_requesting,
            'notis':notifications,'frequests':frequests,
        }

        return render(request, 'social/profile.html', context)


class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','city','picture','public']
    template_name = 'social/profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk':pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollower(LoginRequiredMixin, View):
    def post(self,request,pk,*args,**kwargs):
        a = 0
        user = User.objects.get(pk=pk)

        
        
        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')
        profile = UserProfile.objects.get(pk=pk)
        if profile.public == True:
            profile.followers.add(request.user)
            request.user.profile.following.add(user)
            new_notification = Notification()
            new_notification.sender = request.user
            new_notification.receiver = user
            new_notification.type = 5
            new_notification.save()
        else:
            for fr in frequests:
                if fr.sender == request.user:
                    fr.is_active = False
                    fr.delete()
                    
                    a = 1
            if a == 0:
                new_post = FollowRequest()
                new_post.sender = request.user
                new_post.receiver = user
                new_post.is_active = True
                profile.follow_requests = profile.follow_requests+1
                profile.save()
                new_post.save()
        

        
        return redirect('profile',pk=profile.pk)


class NotificationsView(LoginRequiredMixin, View):
    def get(self,request,pk,*args,**kwargs):
        user = User.objects.get(pk=pk)
        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')
        notis = Notification.objects.filter(receiver=user, is_active=True).order_by('-timestamp')

        for noti in notis:
            if noti.sender == noti.receiver:
                notis.exclude(id=noti.id)

        requests_count = len(notis) + len(frequests)

        context = {
            'count' : requests_count,
            'notifications' : notis,
            'frequests':frequests,
        }
        

        return render(request, 'social/follow_requests.html', context)



class AcceptFollowerView(LoginRequiredMixin,View):
    def post(self,request,receiver_pk, sender_pk ,*args,**kwargs):
        receiver = User.objects.get(pk=request.user.pk)
        sender = User.objects.get(pk=sender_pk)
        
        frequests = FollowRequest.objects.filter(receiver=receiver, is_active=True, sender= sender).order_by('-timestamp')
        receiver.profile.follow_requests = receiver.profile.follow_requests-1
        
        
        for r in frequests:
            r.is_active = False
            r.delete()
        
        sender.profile.following.add(receiver)
        receiver.profile.followers.add(sender)
        
        return redirect('post-list')

class RejectFollowerView(LoginRequiredMixin,View):
    def post(self,request,receiver_pk, sender_pk ,*args,**kwargs):
        receiver = User.objects.get(pk=request.user.pk)
        sender = User.objects.get(pk=sender_pk)
       
        receiver.profile.follow_requests = receiver.profile.follow_requests-1
       
        frequests = FollowRequest.objects.filter(receiver=receiver, is_active=True, sender= sender).order_by('-timestamp')
        
        for r in frequests:
            r.is_active = False
            r.delete()

        
        
        return redirect('post-list')


class RemoveFollowerView(LoginRequiredMixin, View): #remove follower
    def post(self,request,pk,*args,**kwargs):
        user = User.objects.get(pk=request.user.pk)
        to_remove = User.objects.get(pk=pk)
        user.profile.followers.remove(to_remove)
        to_remove.profile.following.remove(request.user)

        return redirect('list-followers',pk=user.pk)


class RemoveFollower(LoginRequiredMixin,View): # unfollow
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        request.user.profile.following.remove(request.user)

        return redirect('profile',pk=profile.pk)



class RemoveNotificationView(LoginRequiredMixin,View):
    def post(self,request,noti_pk,*args,**kwargs):

        Notification.objects.get(id=noti_pk).delete()
        
        

        return redirect('follow-requests', pk=request.user.pk)

class RemoveAllNotificationView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        
        notis = Notification.objects.filter(receiver=request.user).delete()
        
        
        
        

        return redirect('follow-requests', pk=request.user.pk)
        



class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)


        log_user = User.objects.get(username=request.user.username)
       

        if request.user != post.author:
            new_notification = Notification()
            new_notification.sender = log_user
            new_notification.receiver = post.author
            
            new_notification.post = post
        


        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)
            post.likes_count = F('likes_count') + 1
            if request.user != post.author:
                new_notification.type = 1
                new_notification.save()
            
        
            

        if is_like:
            post.likes.remove(request.user)
            post.likes_count = F('likes_count') - 1
            if request.user != post.author:
                new_notification.type = 4
                new_notification.save()
        post.save()
        
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

class AddReport(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        
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

        if date == "" and city == "" and words == "":
            post_list = Post.objects.filter( Q(title__icontains=words) and Q(body__icontains=words)).order_by('-created_on')

        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post_list' : post_list,
             'is_user' : user,
             'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/search.html' , context)


class ListFollowers(View):
    def get(self,request,pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()
        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
        'profile': profile,
        'followers':followers,
        'notis':notifications,'frequests':frequests,
        }

        return render(request , 'social/followers_list.html',context)

class ListFollowing(View):
    def get(self,request,pk,*args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        following = profile.following.all()
        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
        'profile': profile,
        'followers':following,
        'notis':notifications,'frequests':frequests,
        }

        return render(request , 'social/following_list.html',context)



class ListSavedPosts(LoginRequiredMixin, View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        posts = Post.objects.all().order_by('-created_on')

        notis = Notification.objects.filter(receiver=request.user)

         
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post_list' : posts,
            'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/saved_posts.html' , context)

class ListLikedPosts(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        posts = Post.objects.all().order_by('-created_on')
        logged_in_user = request.user
        notis = Notification.objects.filter(receiver=request.user)

        

        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post_list' : posts,'notis':notifications,'frequests':frequests,
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


        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post_list' : posts,'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/fav_posts.html' , context)

class ListPopularPosts(View):
    def get(self,request,*args,**kwargs):
        notis = Notification.objects.filter(receiver=request.user)

        



        posts = Post.objects.all().order_by('-likes_count')
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'post_list' : posts,'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/popular_posts.html' , context)


        

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': 2000,
                        'product_data': {
                            'name': 'product name',
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            
            mode='payment',
            success_url=YOUR_DOMAIN + 'social/success/',
            cancel_url=YOUR_DOMAIN + 'social/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
            })
        



class ProductLandingView(TemplateView):
    template_name = "social/products.html"
    def get_context_data(self, **kwargs):
        product = Product.objects.get()
        context = super(ProductLandingView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context
    
        
        


class SuccessView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'social/success.html')


class  CancelView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'social/cancel.html')








@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

        # TODO - decide whether you want to send the file or the URL
    
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. Here is the product you ordered. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="matt@test.com"
        )

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = (request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='eur',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })







class FriendsView(View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)

        followers = profile.followers.all()
        print(followers)
        for follower in followers:
            if follower in request.user.profile.following.all():
                print("amigos")
            else:
                print("não amigos")
                followers.exclude(pk=follower.pk)
            print(follower)

        

        notis = Notification.objects.filter(receiver=request.user)

          
        logged_in_user = request.user
        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            
            'followers' : followers,'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/friends.html' , context)

class FriendsSearch(View):
    def get(self,request,*args,**kwargs):
        name = self.request.GET.get('name')
        is_user_profile = False
        is_user = False


        if name == "":
            user_list = []



        elif list(name)[0] == "@":
            name = name.replace("@","")
            user_list = User.objects.filter(Q(username__icontains=name)).order_by('-username')
            is_user = True
            
        else:
            
            user_list = User.objects.filter(Q(profile__name__icontains=name)).order_by('-username')
            
            is_user_profile = True

        notis = Notification.objects.filter(receiver=request.user)

        
        logged_in_user = request.user

        frequests = FollowRequest.objects.filter(receiver=logged_in_user, is_active=True).order_by('-timestamp')
        notifications = len(notis) + len(frequests)

        context = {
            'user_list' : user_list,
            'is_user' : is_user,
            'is_user_profile': is_user_profile,'notis':notifications,'frequests':frequests,
        }
        
        return render(request, 'social/friends_search.html' , context)




