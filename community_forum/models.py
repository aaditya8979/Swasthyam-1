"""
Community Forum models - Posts, Comments, Likes, Reports.
Designed for real-time interactions and moderation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """Forum categories for organizing posts"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='💬', help_text=_("Emoji or icon class"))
    color = models.CharField(max_length=7, default='#22c55e', help_text=_("Hex color code"))
    order = models.PositiveIntegerField(default=0, help_text=_("Display order"))
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def post_count(self):
        return self.posts.count()


class Post(models.Model):
    """
    Forum post model with tagging and moderation.
    """
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
        ('flagged', _('Flagged for Review')),
    ]
    
    # Core fields
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    content = models.TextField()
    
    # Maternal health specific
    is_maternal_related = models.BooleanField(default=False, help_text=_("Show in Maternal Health forum"))
    pregnancy_week = models.PositiveIntegerField(null=True, blank=True, help_text=_("Relevant pregnancy week"))
    
    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    # Engagement
    pinned = models.BooleanField(default=False, help_text=_("Pin to top of forum"))
    locked = models.BooleanField(default=False, help_text=_("Prevent new comments"))
    
    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ['-pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:240]
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('community_forum:post_detail', kwargs={'slug': self.slug})
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    @property
    def like_count(self):
        return self.likes.count()
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def is_liked_by(self, user):
        """Check if user has liked this post"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Comment(models.Model):
    """Comments on forum posts"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    @property
    def like_count(self):
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if user has liked this comment"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Like(models.Model):
    """Like system for posts and comments"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        unique_together = [
            ['user', 'post'],
            ['user', 'comment'],
        ]
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['user', 'comment']),
        ]
    
    def __str__(self):
        if self.post:
            return f"{self.user.username} likes post: {self.post.title}"
        return f"{self.user.username} likes comment"


class Report(models.Model):
    """Moderation system for inappropriate content"""
    
    REASON_CHOICES = [
        ('spam', _('Spam')),
        ('harassment', _('Harassment')),
        ('misinformation', _('Misinformation')),
        ('inappropriate', _('Inappropriate Content')),
        ('off_topic', _('Off Topic')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('reviewed', _('Reviewed')),
        ('actioned', _('Action Taken')),
        ('dismissed', _('Dismissed')),
    ]
    
    # What is being reported
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    # Report details
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, help_text=_("Additional details"))
    
    # Moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    moderator_notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")
        ordering = ['-created_at']
    
    def __str__(self):
        if self.post:
            return f"Report on post: {self.post.title}"
        return f"Report on comment by {self.comment.author.username}"


class Bookmark(models.Model):
    """Save posts for later reading"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Bookmark")
        verbose_name_plural = _("Bookmarks")
        unique_together = ['user', 'post']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"