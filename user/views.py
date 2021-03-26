from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login as log, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .form import LoginForm, RegisterForm
from .models import Auct, Feed
from managing.views import addAuction, tip, permanentSaving, getWorkflow
from datetime import datetime
from django.conf import settings

def checkAuct(request):
    print('ciao')
    info = Request.GET
    print(info.data)
    retData = {"info": "ciao"}
    return JsonResponse(retData)


@login_required(login_url='/login') #the non-logged in user is redirected to the login page
def homePage(request):
    if request.method == 'POST':
        form = request.POST
        if 'feed' in form:
            eml = form['email']
            content = form['feed']
            newFeed = Feed.objects.create(user=request.user, content=content)
            newFeed.save()
            nwrk = []
            auctions = Auct.objects.filter(active=True).values()
            wrk = getWorkflow()
            for item in wrk:
                nwrk.append(item.decode('utf-8'))
            return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
        else:
            identifAuct = form['identif']
            tipPrice = form['bet']
            identifUser = request.user.username
            x = datetime.now()
            dateBet = datetime.strftime(x, "%Y-%m-%d %H:%M")
            thisPriceAuct = Auct.objects.filter(id=int(identifAuct)).values()[0]
            if float(tipPrice) < thisPriceAuct['price']:
                messages.warning(request, "Bid too low!!")
                auctions = Auct.objects.filter(active=True).values()
                nwrk = []
                wrk = getWorkflow()
                for item in wrk:
                    nwrk.append(item.decode('utf-8'))
                return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
            else:
                #save offer on Redis
                tip(identifAuct, tipPrice, identifUser, dateBet)

                #update the offered price
                updatePriceAuct = Auct.objects.get(id=int(identifAuct))
                updatePriceAuct.price = float(tipPrice)
                updatePriceAuct.buyer = request.user
                updatePriceAuct.save()
                nwrk = []
                auctions = Auct.objects.filter(active=True).values()
                wrk = getWorkflow()
                messages.success(request, "Bet placed successfully")
                for item in wrk:
                    nwrk.append(item.decode('utf-8'))
                return render(request, 'user/homePage.html', {'auctions': auctions, 'workflow':nwrk})
    else:
        #check the expired auctions
        x = datetime.now()
        nowDate = datetime.strftime(x, "%Y-%m-%d %H:%M") #now date
        auctions = Auct.objects.filter(active=True).values()
        if auctions is not None:
            for item in auctions:
                corDate = datetime.strftime(item['endData'], "%Y-%m-%d %H:%M") #end datetime
                if nowDate >= corDate:
                    det = Auct.objects.get(id=item['id'])
                    det.active = False
                    det.save()
                    winner = User.objects.get(id=item['buyer_id'])
                    permanentSaving(det, winner)
                    return render(request, 'user/homePage.html', {'auctions': auctions})
        nwrk = []
        wrk = getWorkflow()
        for item in wrk:
            nwrk.append(item.decode('utf-8'))
        return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
            

def retUserId(ident):
    thisUser = User.objects.get(id=ident)
    return thisUser


@login_required(login_url='/login') #the non-logged in user is redirected to the login page
def adminPanel(request):
    if request.method == 'POST':
        form = request.POST
        if form:
            try:
                obj = form['object']
                price = form['price']
                endDate = form['endDate']
                endTime = form['endTime']
                endDateTime = endDate+' '+endTime
                newAuction = Auct.objects.create(nobject=obj, buyer=request.user , price=price, endData=endDateTime)
                aucId = newAuction.id
                newAuction.save()
                nwrk = []
                wrk = getWorkflow()
                for item in wrk:
                    nwrk.append(item.decode('utf-8'))
                messages.success(request, "Auction successfully added!")
                #Save the initial data of this auction on Redis using managing methods
                addAuction(aucId)
                feeds = Feed.objects.filter().values()
                auctions = Auct.objects.filter().values()
                return render(request, 'user/adminPanel.html', {'auctions':auctions, 'feed':feeds, 'workflow':nwrk})
            except:
                messages.warning(request, "New auction creation failed. Check all fields")
                feeds = Feed.objects.filter().values()
                auctions = Auct.objects.filter().values()
                nwrk = []
                wrk = getWorkflow()
                for item in wrk:
                    nwrk.append(item.decode('utf-8'))
                return render(request, 'user/adminPanel.html', {'auctions':auctions, 'feed':feeds, 'workflow':nwrk})
    else:
        feeds = Feed.objects.filter().values()
        auctions = Auct.objects.filter().values()
        nwrk = []
        wrk = getWorkflow()
        for item in wrk:
            nwrk.append(item.decode('utf-8'))
        return render(request, 'user/adminPanel.html', {'auctions':auctions, 'feed':feeds, 'workflow':nwrk})


def login(request):  #User access
    if request.method == 'POST':
        form = request.POST
        if form:
            username = form['username']
            password = form['password']
            try:
                user = authenticate(username=username, password=password)
                if user.is_superuser:
                    messages.success(request, "Login successful. Welcome back administrator!")
                    log(request, user)
                    return redirect('/adminPanel')
                else:
                    messages.success(request, f"Login successful. Welcome back {username}")
                    log(request, user)
                    return redirect('/')
            except:
                messages.warning(request, "Login failed!")
                form = LoginForm()
                return render(request, 'user/login.html', {'form':form})
    else:
        form = LoginForm()
        return render(request, 'user/login.html', {'form':form})


def log_out(request):
    logout(request)
    return redirect("/login")


def registration(request):  #User registration
    if request.method == 'POST':
        form = request.POST
        if form:
            username = form['username']
            email = form['email']
            password = form['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful")
            form = LoginForm()
            return login(request)
        else:
            messages.warning(request, "Registration failed")
            form = RegisterForm()
            return render(request, 'user/registration.html', {'form':form})
    else:
        form = RegisterForm()
        return render(request, 'user/registration.html', {'form':form})


