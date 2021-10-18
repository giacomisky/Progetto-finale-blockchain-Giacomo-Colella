from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login as log, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .form import LoginForm, RegisterForm
from .models import Auct, Feed, Wallet, Storage
from managing import utils
from managing.views import addAuction, tip, permanentSaving, getWorkflow
from datetime import datetime
from django.conf import settings
import random



def getHomeData():
    nwrk = []
    auctions = Auct.objects.filter(active=True).values()
    wrk = getWorkflow()
    for item in wrk:
        nwrk.append(item.decode('utf-8'))
    return auctions, nwrk


#Check every expired auctions
def checkExpiredAuction():
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



@login_required(login_url='/login') #the non-logged in user is redirected to the login page
def homePage(request):
    if request.method == 'POST':
        form = request.POST
        if 'feed' in form:
            email = form['email']
            content = form['feed']
            newFeed = Feed.objects.create(user=request.user, content=content)
            newFeed.save()
            auctions, nwrk = getHomeData()
            return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
        else:
            identifAuct = form['identif']
            tipPrice = form['bet']
            identifUser = request.user.username
            x = datetime.now()
            dateBet = datetime.strftime(x, "%Y-%m-%d %H:%M")
            thisPriceAuct = Auct.objects.filter(id=int(identifAuct)).values()[0]

            #check if the stake is lower than the current price
            #the stake can be equal or bigger than current price
            if float(tipPrice) < thisPriceAuct['price']:
                messages.warning(request, "Bid too low!!")
                auctions, nwrk = getHomeData()
                return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
            else:
                #the stake can be also equal than current price
                getWalletInfo = Wallet.objects.filter(owner=request.user).values()[0]

                #check if the user has sufficient balance
                if getWalletInfo['euroBalance'] < float(tipPrice):
                    messages.warning(request, "Insufficient budget to carry out his bet")
                    auctions, nwrk = getHomeData()
                    return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
                else:
                    #save offer on Redis
                    tip(identifAuct, tipPrice, identifUser, dateBet)

                    #update the offered price
                    updatePriceAuct = Auct.objects.get(id=int(identifAuct))
                    updatePriceAuct.price = float(tipPrice)
                    updatePriceAuct.buyer = request.user
                    updatePriceAuct.save()

                    #update user balance
                    userWallet = Wallet.objects.get(owner=request.user)
                    userWallet.euroBalance -= float(tipPrice)
                    userWallet.save()

                    auctions, nwrk = getHomeData()
                    messages.success(request, "Bet placed successfully")
                    return render(request, 'user/homePage.html', {'auctions': auctions, 'workflow':nwrk})
    else:
        #check the expired auctions
        checkExpiredAuction()
        auctions, nwrk = getHomeData()
        return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': nwrk})
            




def retUserId(ident):
    thisUser = User.objects.get(id=ident)
    return thisUser


def shoWinner(request):
    try:
        infoAuct = Auct.objects.filter(buyer=request.user.id, active=False).values()
        return render(request, 'user/winPage.html', {'infoWin': infoAuct})
    except:
        return render(request, 'user/winPage.html', {})


def shoWallet(request):
    walletInfo = Wallet.objects.get(owner=request.user.id)
    return render(request, 'user/walletPage.html', {'infoWallet':walletInfo})


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
                    checkExpiredAuction()
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

            #create object User
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            #create user Wallet
            randEuroBalance = random.randrange(5000, 30000)
            wallet = utils.createWallet(password)
            thisWallet = Wallet.objects.create(owner=user, address=wallet['address'], privateKey=wallet['cryptKey'], ethBalance=wallet['balance'], euroBalance=randEuroBalance)
            thisWallet.save()

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


