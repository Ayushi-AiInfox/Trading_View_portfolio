from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User=get_user_model()
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from django.views.generic import View
import jwt
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.core.mail import send_mail
from decimal import Decimal
from django.conf import settings
KEYS = getattr(settings, "KEY", None) 



def calculate_portfolio_performance(portfolio, stock_prices):
    total_cost = Decimal(0)
    current_market_value = Decimal(0)
    for holding in portfolio.holdings.all():
        ticker = holding.stock.ticker
        current_price = stock_prices.get(ticker, 0)
        cmv = holding.quantity * Decimal(current_price)
        current_market_value += cmv
        total_cost += holding.quantity * holding.average_price
    if total_cost == 0:
        return 0
    performance = ((current_market_value - total_cost) / total_cost) * 100
    return round(performance, 2)


def LoginView( request):
    message= request.session.get('message')
    message1 = request.session.get("message1")
    try:
        del request.session['message']
    except:
        pass
    try:
        del request.session['message1']
    except:
        pass
    if request.session.has_key('token'):
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified":
                return redirect('../../accounts/login')
            else:
                if d.get("role")=="user":
                    return redirect("../../accounts/user_dashboard")
                elif d.get("role")=="admin":
                    return redirect("../../admin/dashboard")
        except:
            pass
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, "Please fill in both username and password.")
            return redirect('login')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['role'] = user.role
            request.session['username'] = user.username
            payload = {
                'email': user.email,
                'method': 'verified',
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(days=1)
            }         
            token = jwt.encode(payload=payload,key=KEYS,algorithm='HS256')
            request.session['token'] = token
            if user.role == "admin":
                request.session['message']="success"
                return redirect('../../admin/dashboard')
            else:
                request.session['message']="success"
                return redirect('user_dashboard')
        else:
            request.session['message1']="Invalid username or password"
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request,'accounts/login.html',{"message":message,"message1":message1})
        







def SignupView(request):
    if request.session.has_key('token'):
        token = request.session.get('token')
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified":
                return redirect('../../accounts/login')
            else:
                if d.get("role")=="user":
                    return redirect("../../accounts/user_dashboard")
                elif d.get("role")=="admin":
                    return redirect("../../admin/dashboard")
        except:
            pass
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')
            
        if not username or not email or not password1 or not password2:
            messages.error(request, "Please fill in all fields.")
            return redirect('signup')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        try:
            user = User.objects.create(username=username, email=email, password=make_password(password1))
            user.save()
            request.session['username'] = user.username
            request.session['role'] = 'user'
            messages.success(request, "Signup successful!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('signup')
    return render(request,'accounts/signup.html')    



def UserDashboardView(request):
    if request.session.has_key('token'):
        token = request.session.get('token')
        print(token)
        try:
            d = jwt.decode(token, key=KEYS, algorithms=['HS256'])
            usr = User.objects.get(email = d.get("email"))
            if d.get('method')!="verified" or usr.role!='user':
                return redirect('../../accounts/user_dashboard')
        except:
            return redirect('../../accounts/login')
        if 'message' in request.session:
            messages.success(request, "Login successful!")
            del request.session['message'] 
        return render(request, 'user_dashboard.html', {'symbol': 'AAPL'})
    else:
        return redirect("../../accounts/login")


def LogoutView(request):
    message3= request.session.get('message')
    try:
        del request.session['message']
    except:
        pass


    try:
        del request.session['token']
    except KeyError:
        pass
    messages.success(request, "You have successfully logged out.")
    request.session['message']="success"
    
    return redirect('../../accounts/login')




def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Please enter your email.")
            return redirect('password_reset')
        
        try:
            # Check if the email exists in the system
            user = User.objects.get(email=email)
            
            # Generate JWT token for password reset
            payload = {
                'email': user.email,
                'method': 'reset_password',
                'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            }
            token = jwt.encode(payload=payload, key=KEYS, algorithm='HS256')

            # Send password reset email with the token
            reset_url = request.build_absolute_uri(f'/accounts/password_reset_confirm/{token}/')
            print(reset_url,"----")
            send_mail(
                'Password Reset Request',
                f'Click the link below to reset your password:\n\n{reset_url}',
                'admin@example.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('../../accounts/password_reset/')

        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect('password_reset')
    
    return render(request, 'accounts/password_reset.html')



def password_reset_confirm(request, token):
    try:
        # Decode and verify the token
        decoded_token = jwt.decode(token, key=KEYS, algorithms=['HS256'])
        email = decoded_token.get('email')
        method = decoded_token.get('method')
        
        if method != 'reset_password':
            messages.error(request, "Invalid token.")
            return redirect('login')
        
        # Check if the user with the decoded email exists
        user = User.objects.get(email=email)
        
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            # Ensure that the password and confirm password match
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect('password_reset_confirm', token=token)

            # Set the new password
            user.set_password(new_password)
            user.save()

            messages.success(request, "Your password has been successfully reset!")
            return redirect('login')

        return render(request, 'accounts/password_reset_confirm.html', {'token': token})

    except jwt.ExpiredSignatureError:
        messages.error(request, "The password reset link has expired.")
        return redirect('password_reset')

    except jwt.DecodeError:
        messages.error(request, "Invalid token.")
        return redirect('login')

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')
