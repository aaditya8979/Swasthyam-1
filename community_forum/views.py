from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Category, Comment, Like, Bookmark, Report
from .forms import PostForm, CommentForm

def forum_home(request):
    # --- AUTO-FIX: Create Categories if missing ---
    if Category.objects.count() == 0:
        defaults = [
            ("Maternal Health", "🤰", "Pregnancy discussions"),
            ("Child Nutrition", "🍎", "Feeding tips"),
            ("Mental Wellness", "🧘‍♀️", "Stress support"),
            ("Vaccinations", "💉", "Reminders & info"),
        ]
        for name, icon, desc in defaults:
            Category.objects.create(name=name, icon=icon, description=desc)
    # ---------------------------------------------
    
    posts = Post.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    return render(request, 'forum/home.html', {'posts': posts, 'categories': categories})

@login_required
def category_posts(request, slug):
    """Filter posts by category."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    
    context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'forum/category_posts.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('community_forum:home')
    else:
        form = PostForm()
    return render(request, 'forum/post_form.html', {'form': form, 'title': 'Create Post'})

@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.increment_views()
    
    comments = post.comments.all().order_by('created_at')
    
    # Handle new comment submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('community_forum:post_detail', slug=slug)
    else:
        form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'is_bookmarked': post.bookmarks.filter(user=request.user).exists(),
        'is_liked': post.likes.filter(user=request.user).exists()
    }
    return render(request, 'forum/post_detail.html', context)

@login_required
def like_post(request, post_id):
    """AJAX endpoint for liking a post."""
    post = get_object_or_404(Post, id=post_id)
    liked = False
    
    existing_like = Like.objects.filter(user=request.user, post=post).first()
    if existing_like:
        existing_like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def bookmark_post(request, post_id):
    """AJAX endpoint for bookmarking."""
    post = get_object_or_404(Post, id=post_id)
    bookmarked = False
    
    existing_bookmark = Bookmark.objects.filter(user=request.user, post=post).first()
    if existing_bookmark:
        existing_bookmark.delete()
    else:
        Bookmark.objects.create(user=request.user, post=post)
        bookmarked = True
        
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post')
    return render(request, 'forum/bookmarks.html', {'bookmarks': bookmarks})

# --- Placeholders to prevent crashes (Implement full logic if needed) ---
@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('community_forum:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'forum/post_form.html', {'form': form, 'title': 'Edit Post'})

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('community_forum:home')

# In community_forum/views.py

@login_required
def create_post(request):
    # Check if a category is requested via URL (e.g. from Maternal page)
    initial_data = {}
    cat_slug = request.GET.get('category')
    is_maternal = request.GET.get('is_maternal')
    
    if cat_slug:
        category = Category.objects.filter(slug=cat_slug).first()
        if category:
            initial_data['category'] = category
            
    if is_maternal:
        initial_data['is_maternal_related'] = True

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('community_forum:home')
    else:
        form = PostForm(initial=initial_data)
        
    return render(request, 'forum/post_form.html', {'form': form, 'title': 'Create Post'})

# Stub functions for other URLs to prevent ImportErrors
@login_required
def add_comment(request, post_id): pass
@login_required
def edit_comment(request, comment_id): pass
@login_required
def delete_comment(request, comment_id): pass
@login_required
def like_comment(request, comment_id): pass
@login_required
@login_required
def report_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    # Hide from public immediately
    post.is_active = False 
    post.save()
    messages.warning(request, "Post reported and hidden for review.")
    return redirect('community_forum:home')
@login_required
def report_comment(request, comment_id): 
    return JsonResponse({'success': True}) # Placeholder