from app_job_hunt.forms import RawContactEmployerForm


def add_raw_contact_employer_form(request):
    data = {
        'raw_contact_employer_form': RawContactEmployerForm(),
    }

    return data