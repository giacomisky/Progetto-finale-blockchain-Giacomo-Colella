from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login as log, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .form import LoginForm, RegisterForm
from .models import Auct

from managing.views import addAuction, tip, permanentSaving, getWorkflow
from datetime import datetime
from auctionProject.settings import EMAIL_HOST_USER



@login_required(login_url='/login') #the non-logged in user is redirected to the login page
def homePage(request):
    if request.method == 'POST':
        form = request.POST
        
        identifAuct = form['identif']
        tipPrice = form['bet']
        identifUser = request.user.username

        x = datetime.now()
        dateBet = datetime.strftime(x, "%Y-%m-%d %H:%M")

        thisPriceAuct = Auct.objects.filter(id=int(identifAuct)).values()[0]
        if float(tipPrice) < thisPriceAuct['price']:
            http = HttpResponse()
            http.write("<dialog open><p>Bid too low!</p></dialog>") #-------------DA SISTEMARE
            return http
        else:
            #save offer on Redis
            tip(identifAuct, tipPrice, identifUser, dateBet)

            #update the offered price
            updatePriceAuct = Auct.objects.get(id=int(identifAuct))
            updatePriceAuct.price = float(tipPrice)
            updatePriceAuct.buyer = request.user
            updatePriceAuct.save()

            auctions = Auct.objects.filter(active=True).values()
            wrk = getWorkflow()
            return render(request, 'user/homePage.html', {'auctions': auctions, 'workflow':wrk})
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
            
        wrk = getWorkflow()
        return render(request, 'user/homePage.html', {'auctions':auctions, 'workflow': wrk})
            
            


def adminPanel(request):
    if request.method == 'POST':
        form = request.POST
        if form:
            obj = form['object']
            price = form['price']
            endDate = form['endDate']
            endTime = form['endTime']
            
            endDateTime = endDate+' '+endTime
            
            newAuction = Auct.objects.create(nobject=obj, buyer=request.user , price=price, endData=endDateTime)
            aucId = newAuction.id
            newAuction.save()
            
            #Save the initial data of this auction on Redis using managing methods
            addAuction(aucId)
            
            auctions = Auct.objects.filter().values()
            return render(request, 'user/adminPanel.html', {'auctions':auctions})
    else:
        auctions = Auct.objects.filter().values()
        return render(request, 'user/adminPanel.html', {'auctions':auctions})




def login(request):  #User access
    if request.method == 'POST':
        form = request.POST
        if form:
            username = form['username']
            password = form['password']
            try:
                user = authenticate(username=username, password=password)
                if user.is_superuser:
                    log(request, user)
                    return redirect('/adminPanel')
                else:
                    log(request, user)
                    return redirect('/')
            except:
                http = HttpResponse()
                http.write("<dialog open><p>Data given not valid!</p></dialog>")
                return http
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

            #Confirm email sent
            send_mail('You are registered!', f"Thanks {username} for subscribing to the platform", EMAIL_HOST_USER, [email], fail_silently=False)
            form = LoginForm()
            return login(request)
        else:
            http = HttpResponse()
            http.write("<h2>You are just registered on this platform!</h2>") 
            return http
    else:
        form = RegisterForm()
        return render(request, 'user/registration.html', {'form':form})
