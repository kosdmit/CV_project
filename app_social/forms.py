from django import forms

from app_social.models import Comment, Post


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


class PostCreateForm(forms.Form):
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'messageHelp',
                                     'placeholder': 'Что у вас нового? Добавьте сообщение в блог!',
                                     'rows': '3'}),
    )


class PostForm(forms.ModelForm):
    message = forms.CharField(
        required=True,
        label='Введите текст сообщения:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'messageHelp',
                                     'rows': '3'}),
    )

    image = forms.FileField(
        required=False,
        label='Прикрепите изображение:',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Post
        fields = ['message', 'image']


class ResumeSearchForm(forms.Form):
    search_query = forms.CharField(
        widget=forms.TextInput(attrs={'class': "form-control",
                                      'placeholder': "Найти...",
                                      'aria-label': "Search"})
    )
