from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'is_maternal_related', 'pregnancy_week']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Give your post a descriptive title'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500 h-40',
                'placeholder': 'Share your thoughts...'
            }),
            'pregnancy_week': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500'
            }),
            'is_maternal_related': forms.CheckboxInput(attrs={
                'class': 'rounded text-green-600 focus:ring-green-500'
            })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-green-500 focus:border-green-500 h-24',
                'placeholder': 'Write a supportive comment...',
                'rows': 3
            })
        }