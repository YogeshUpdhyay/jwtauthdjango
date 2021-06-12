
import json
import datetime
from jose import jwt
from functools import wraps
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect, HttpResponseServerError
from user.forms import LoginForm, SignUpForm, UpdateUserForm
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage

import config
from user.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = args[0].COOKIES.get('token')
        if not token:
            print("Here")
            return redirect("login")
        try:
            data = decode(token)
        except Exception as e:
            print(e)
            return redirect("login")
        kwargs['id'] = json.loads(data['sub'])['id']
        return f(*args, **kwargs)
    return decorated

def encode(payload):
    _token_schema = {
        'iat': datetime.datetime.now(),
        'exp': datetime.datetime.now() + datetime.timedelta(seconds=config.ACCESS_TOKEN_EXPIRATION),
        'sub': json.dumps(payload)
    }
    return jwt.encode(
        _token_schema,
        config.SECRET_KEY,
        algorithm=config.ALGORITHM
    )

def decode(token):
    return jwt.decode(
        token,
        config.SECRET_KEY
    )

# Create your views here.
def login(request):
    # if login form is submitted
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.filter(email = data.get("email")).first()

            if user is None:
                messages.error(request, 'Email not found!')
                return HttpResponseRedirect(reverse_lazy('login'))

            if not user.verifypass(data.get("password")):
                messages.error(request, 'Invalid Password!')
                return HttpResponseRedirect(reverse_lazy('login'))

            payload = {'id': user.id}
            token = encode(payload)
            response = redirect('user', 1)
            response.set_cookie(key='token', value=token)

            return response

    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):

    # if registeration form is submitted
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if data['password1'] != data['password2']:
                messages.error(request, 'Invalid Password!')
                return HttpResponseRedirect(reverse_lazy('register'))

            user = User.objects.filter(email = data['email']).first()

            if user:
                messages.error(request, 'User already exists!')
                return HttpResponseRedirect(reverse_lazy('register'))

            data['password'] = str(data['password2'])
            del data['password1']
            del data['password2']

            user = User(**data)
            user.hashpass(data['password'])
            user.save()
            
            payload = {'id': user.id}
            token = encode(payload)
            response = redirect('user', 1)
            response.set_cookie(key='token', value=token)

            return response
        else:
            messages.error(request, 'Invalid Credentials!')
            return HttpResponseRedirect(reverse_lazy('register'))

    form = SignUpForm()
    return render(request, 'register.html', {'form': form})

@token_required
def logout(request, id):
    response = HttpResponseRedirect("/login")
    response.delete_cookie('token')
    return response

@token_required
def user_detail(request, id, page_no = 1):
    queryset = User.objects.all()
    users = [user.payload() for user in queryset]
    p = Paginator(users, 8)
    try:
        page = p.page(page_no)
    except EmptyPage:
        page = p.page(1)
    content = {'page': page, 'previous_page': page_no-1, 'next_page': page_no+1}
    return render(request, 'index.html', content)

@token_required
def update_user(request, id, slug):
    # user details
    if request.method == "POST":
        try:
            form = UpdateUserForm(request.POST)
            if form.is_valid():
                data = form.get_data()
                print(data)
                user = User.objects.filter(id = slug)
                user.update(**data)
                messages.success(request, 'Successfully updated!')
                page_no = int((request.headers['Referer']).split("/")[-1])
                return HttpResponseRedirect(reverse_lazy('user', kwargs={'page_no': page_no}))
            else:
                messages.error(request, 'Invalid Value!')
                page_no = int((request.headers['Referer']).split("/")[-1])
                return HttpResponseRedirect(reverse_lazy('user', kwargs={'page_no': page_no}))
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        page_no = int((request.headers['Referer']).split("/")[-1])
        return HttpResponseRedirect(reverse_lazy('user', kwargs={'page_no': page_no}))

@token_required
def delete_user(request, id, slug):
    user = User.objects.get(id = slug)
    
    user.delete()
    messages.success(request, 'Successfully deleted!')
    page_no = int((request.headers['Referer']).split("/")[-1])
    return HttpResponseRedirect(reverse_lazy('user', kwargs={'page_no': page_no}))

        