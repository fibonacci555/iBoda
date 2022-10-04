from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Count, F
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from .models import Post, Comment, UserProfile, Product, FollowRequest
from .forms import PostForm, CommentForm
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

stripe.api_key = settings.STRIPE_SECRET_KEY











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

        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')

        is_requesting = False


        for req in frequests:
            if req.sender == request.user and req.is_active:
                is_requesting = True


        for post in posts:
            print(post.favs.all())
            for user in post.favs.all():

                profile.favs_count = profile.favs_count + 1

        followers = profile.followers.all()


        n_followers = len(followers)
        is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        fav_counter = profile.favs_count
        context = {
            'user' : user,
            'profile' : profile,
            'posts' : posts,
            'n_followers' : n_followers,
            'followers' : followers,
            'is_following' : is_following,
            'fav_counter' : fav_counter,
            'is_requesting' : is_requesting,
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
        a = 0
        user = User.objects.get(pk=pk)
        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')
        profile = UserProfile.objects.get(pk=pk)
        if profile.public == True:
            print('public')
            profile.followers.add(request.user)
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


class FollowRequestsView(LoginRequiredMixin, View):
    def get(self,request,pk,*args,**kwargs):
        user = User.objects.get(pk=pk)
        
        frequests = FollowRequest.objects.filter(receiver=user, is_active=True).order_by('-timestamp')

        requests_count = len(frequests)

        context = {
            'count' : requests_count,
            'requests' : frequests,
        }
        

        return render(request, 'social/follow_requests.html', context)



class AcceptFollowerView(LoginRequiredMixin,View):
    def post(self,request,receiver_pk, sender_pk ,*args,**kwargs):
        receiver = User.objects.get(pk=request.user.pk)
        sender = User.objects.get(pk=sender_pk)

        frequests = FollowRequest.objects.filter(receiver=receiver, is_active=True, sender= sender).order_by('-timestamp')
        
        for r in frequests:
            r.is_active = False
            r.delete()

        receiver.profile.followers.add(sender)
        
        return redirect('follow-requests',pk=receiver.pk)

class RejectFollowerView(LoginRequiredMixin,View):
    def post(self,request,receiver_pk, sender_pk ,*args,**kwargs):
        receiver = User.objects.get(pk=request.user.pk)
        sender = User.objects.get(pk=sender_pk)

        frequests = FollowRequest.objects.filter(receiver=receiver, is_active=True, sender= sender).order_by('-timestamp')
        
        for r in frequests:
            r.is_active = False
            r.delete()

        
        
        return redirect('follow-requests',pk=receiver.pk)


class RemoveFollowerView(LoginRequiredMixin, View):
    def post(self,request,pk,*args,**kwargs):
        user = User.objects.get(pk=request.user.pk)
        to_remove = User.objects.get(pk=pk)
        user.profile.followers.remove(to_remove)

        return redirect('list-followers',pk=user.pk)


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
            post.likes_count = F('likes_count') + 1
            

        if is_like:
            post.likes.remove(request.user)
            post.likes_count = F('likes_count') - 1
        post.save()

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
        print(post.reports.all())

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

class ListPopularPosts(View):
    def get(self,request,*args,**kwargs):
        


        posts = Post.objects.all().order_by('-likes_count')
        print(posts)

        context = {
            'post_list' : posts,
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
        return render(request, 'social/success.html', context)


class  CancelView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'social/cancel.html', context)








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
            req_json = json.loads(request.body)
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


class RegisterView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        return render(request, 'account/signup.html')

    def post(self, request, pk, *args, **kwargs):
        
        form = RegisterForm(request.POST)
        

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



class NotificationsView(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'social/notifications.html')

class FriendsView(View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)

        followers = profile.followers.all()
        

        context = {
            
            'followers' : followers,
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
            print(name)
            user_list = User.objects.filter(Q(profile__name__icontains=name)).order_by('-username')
            print(user_list)
            is_user_profile = True




        context = {
            'user_list' : user_list,
            'is_user' : is_user,
            'is_user_profile': is_user_profile,
        }
        
        return render(request, 'social/friends_search.html' , context)



"""class PostNotification(View):
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

        return HttpResponse('Success', content_type='text/plain')"""
