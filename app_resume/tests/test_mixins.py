from uuid import uuid4

from django.contrib.auth.models import User

from app_resume.models import Resume
from app_users.models import Profile, SocialLinks


class CreateMethodsMixin:
    def create_resume(self, *args, **kwargs):
        resume = Resume.objects.create(user=self.user, profile=self.profile,
                                       slug=str(uuid4())[:4],
                                       position=str(uuid4())[:4])
        for key, value in kwargs.items():
            resume.__setattr__(key, value)

        resume.save()
        return resume


    def create_user(self, *args, **kwargs):
        self.user = User.objects.create_user(username=str(uuid4())[:4], password='testpassword')
        self.profile = Profile.objects.create(user=self.user)
        self.social_links = SocialLinks.objects.create(user=self.user, profile=self.profile)

        for key, value in kwargs.items():
            self.user.__setattr__(key, value)

        self.user.save()
        return self.user