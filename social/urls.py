
from django.urls import path
from .views import RemoveNotificationView,CreatePostView,RemoveFollowerView, RejectFollowerView, AcceptFollowerView, NotificationsView, FriendsSearch , FriendsView, StripeIntentView,stripe_webhook,SuccessView ,CancelView, ProductLandingView, CreateCheckoutSessionView, ListFavPosts, ListPopularPosts ,AddFav,ListLikedPosts, ListSavedPosts, AddSave, AddReport, CommentReplyView, PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, AddLike, AllSearch, ListFollowers
urlpatterns = [ 
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like', AddLike.as_view(), name='like'),
    path('post/<int:pk>/report',  AddReport.as_view(), name='report'),
    path('post/<int:pk>/save',  AddSave.as_view(), name='save'),
    path('post/<int:pk>/fav',  AddFav.as_view(), name='fav'),
    path('create-post/', CreatePostView.as_view(), name='create-post' ),

    path('profile/<int:pk>/fav-posts/', ListFavPosts.as_view(), name='fav-posts'),
    path('profile/<int:pk>/liked-posts/', ListLikedPosts.as_view(), name='liked-posts'),
    path('profile/<int:pk>/saved-posts/', ListSavedPosts.as_view(), name='saved-posts'),
    path('popular-posts/', ListPopularPosts.as_view(), name='popular-posts'),

    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/<int:pk>/followers/remove-follower', RemoveFollowerView.as_view(), name='remove-followers'),

    path('search/', AllSearch.as_view(), name='all-search'),

    path('friends/<int:pk>',FriendsView.as_view(), name='friends'),
    path('friends/<int:pk>/search/', FriendsSearch.as_view(), name='friends-search'),
    #path('notifications/', FriendsSearch.as_view(), name='friends-search'),

    path('friend/<int:pk>/notifications/', NotificationsView.as_view(), name='follow-requests'),
    path('friend/<int:pk>/notifications/remove-notification/<int:noti_pk>', RemoveNotificationView.as_view(), name='remove-noti'),
    path('friend/<int:receiver_pk>/friend-requests/accept/<int:sender_pk>', AcceptFollowerView.as_view(), name='accept'),
    path('friend/<int:receiver_pk>/friend-requests/reject/<int:sender_pk>', RejectFollowerView.as_view(), name='reject'),
    
    #path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name='post-notification'),
    #path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(), name='follow-notification'),
    #path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),


    #path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    #path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    #path('cancel/', CancelView.as_view(), name='cancel'),
    #path('success/', SuccessView.as_view(), name='success'),
    #path('products/', ProductLandingView.as_view(), name='landing-page'),
    #path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),



    
]
