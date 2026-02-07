"""
URL patterns for the community forum app.
"""

from django.urls import path
from . import views

app_name = 'community_forum'

urlpatterns = [
    path('', views.forum_home, name='home'),
    path('category/<slug:slug>/', views.category_posts, name='category'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    
    # Comments (HTMX endpoints)
    path('api/post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('api/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('api/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Likes (AJAX)
    path('api/post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('api/comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    
    # Bookmarks
    path('api/post/<int:post_id>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Reports
    path('api/post/<int:post_id>/report/', views.report_post, name='report_post'),
    path('api/comment/<int:comment_id>/report/', views.report_comment, name='report_comment'),
]