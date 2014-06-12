import json
from google.appengine.api import mail
from django.conf import settings
from django.http.response import HttpResponse
from application import utils
from application.exceptions import Http400, Http404, Http403
from application.responses import JsonResponse
from application.decorators import authorization
from application.forms.search_form import SearchForm
from application.forms.user_form import UserForm
from application.models.dto.page_list import PageList
from application.models.datastore.user_model import UserModel, UserPermission


@authorization(UserPermission.root)
def get_users(request):
    form = SearchForm(**request.GET.dict())
    query = UserModel.all().order('create_time')
    total = query.count()
    applications = query.fetch(utils.default_page_size, form.index.data * utils.default_page_size)
    return JsonResponse(PageList(form.index.data, utils.default_page_size, total, applications))

@authorization(UserPermission.root)
def invite_user(request):
    form = UserForm(name='invite', **json.loads(request.body))
    if not form.validate():
        raise Http400

    users = UserModel.all().filter('email =', form.email.data).fetch(1)
    if len(users):
        # the user is exist
        user = users[0]
    else:
        user = UserModel(
            name=form.email.data,
            email=form.email.data,
            permission=UserPermission.normal,
        )
        user.save()
        gae_account = getattr(settings, 'GAE_ACCOUNT')
        domain = getattr(settings, 'HOST')
        message = mail.EmailMessage(sender=gae_account, subject="%s has invited you to join Victorique." % request.user.name)
        message.to = user.email
        message.body = 'Victorique https://%s\n\nAccount: %s' % (domain, user.email)
        message.send()
    return JsonResponse(user)

@authorization(UserPermission.root)
def delete_user(request, user_id):
    user_id = long(user_id)
    if request.user.key().id() == user_id:
        raise Http403
    user = UserModel.get_by_id(user_id)
    if user is None:
        raise Http404
    user.delete()
    return HttpResponse()

@authorization(UserPermission.root)
def get_user(request, user_id):
    user_id = long(user_id)
    user = UserModel.get_by_id(user_id)
    if user is None:
        raise Http404
    return JsonResponse(user)

@authorization(UserPermission.root)
def update_user(request, user_id):
    user_id = long(user_id)
    form = UserForm(**json.loads(request.body))
    if not form.validate():
        raise Http400
    user = UserModel.get_by_id(user_id)
    if user is None:
        raise Http404
    user.name = form.name.data
    user.permission = form.permission.data
    user.put()
    return JsonResponse(user)