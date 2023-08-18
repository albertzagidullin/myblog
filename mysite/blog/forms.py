from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    """форма позволяющая делиться постами
        name - экземпляр для использования имени человека отправляющего пост
        email - здесь используется емаил человека,отправившего пост
        to - емаил получателя с постом
        comments - он используется для коммента"""
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = forms.CharField()