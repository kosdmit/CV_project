from app_social.forms import ResumeSearchForm


def add_resume_search_form(request):
    data = {
        'resume_search_form': ResumeSearchForm(),
    }

    return data
