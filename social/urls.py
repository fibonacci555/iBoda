
from django.urls import path
from .views import ListFavPosts, AddFav,ListLikedPosts, ListSavedPosts, AddSave, AddReport, CommentReplyView, PostListView, PostDetailView, PostEditView, PostDeleteView, CommentDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, AddLike, AllSearch, ListFollowers
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

    path('profile/<int:pk>/fav-posts/', ListFavPosts.as_view(), name='fav-posts'),
    path('profile/<int:pk>/liked-posts/', ListLikedPosts.as_view(), name='liked-posts'),
    path('profile/<int:pk>/saved-posts/', ListSavedPosts.as_view(), name='saved-posts'),

    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),

    path('search/', AllSearch.as_view(), name='all-search'),
    


    
]
