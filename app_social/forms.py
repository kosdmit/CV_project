from django import forms

from app_social.models import Comment


class CommentForm(forms.ModelForm):
    message = forms.CharField(
        label="Добавить комментарий:",
        widget=forms.Textarea(attrs={'class': 'form-control',
                                      'rows': '3',
                                      'placeholder': "Введите текст комментария"}),
    )

    class Meta:
        model = Comment
        fields = ['message']

class CommentUpdateForm(forms.ModelForm):
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': '3',
                                     'placeholder': "Введите текст комментария"}),
    )

    class Meta:
        model = Comment
        fields = ['message']
