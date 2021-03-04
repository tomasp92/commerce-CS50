from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Auction, Bid, Coment, Category, Watch_list
from django import forms
from django.db.models import When


def filter_sold_render_images(category, *userid):
    if category == "no":
        auctions = Auction.objects.filter(sold=False)   
    elif category == "watchlist":
        watch_list = Watch_list.objects.filter(user=userid,watch=True)
        watchlist = []
        for watchedauction in watch_list:
            watchlist.append(watchedauction.auction.id)
        auctions = Auction.objects.filter(pk__in=watchlist)
    else:
        auctions = Auction.objects.filter(sold=False, category_name=category)
        
    for auction in auctions:
        if auction:    
            auction.auction_image = auction.auction_image[66:]
            try:    
                bid = Bid.objects.get(auction_product=auction.id)
                auction.starting_bid = bid.last_bid
            except:
                pass
    return (auctions)


def index(request):
    auctions = filter_sold_render_images("no")
    return render(request, "auctions/index.html", 
    { "auctions": auctions, "bid": Bid.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)    
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
        
def listing(request, user_id, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    coments = Coment.objects.filter(auction=auction_id)
    try:
        auction_in_watchlist = Watch_list.objects.get(auction=auction_id,user=user_id,watch=True)
        watched = True
    except:
        watched = False

    try:    
        bid = Bid.objects.get(auction_product=auction_id)
        current_price = bid.last_bid
    except:
        current_price = auction.starting_bid
        bid = None
    if watched:
        submit = "Remove from Watch List"
    else:
        submit = "Add to Watch list"
    return render(request, "auctions/listing.html", {"auction": auction, "current_price": current_price, "bid": bid, 
    "coments": coments, "image":auction.auction_image[66:], "submit": submit,
    })

def category(request, category):
    # Get category id
    category = Category.objects.get(category_name=category) 
    auctions = filter_sold_render_images(category)
    return render(request, "auctions/index.html", 
    { "auctions": auctions, "bid": Bid.objects.all(), "category": category.category_name
    })

@login_required(login_url="login")
def addcoment(request): 
    usersname = User.objects.get(username=request.POST.get("username"))
    coment = request.POST.get("commenttext")
    auctionid = Auction.objects.get(pk=request.POST.get("auction"))
    newcoment = Coment(user=usersname, auction=auctionid, text=coment)
    newcoment.save()
    return HttpResponseRedirect(reverse("listing", args=(usersname.id, auctionid.id,)))

def categories(request): 
    return render(request, "auctions/categories.html", { "categories": Category.objects.all() 
    })

@login_required(login_url="login")
def NewBid(request):
    auctions = filter_sold_render_images("no")
    # Get Bid Form
    new_bid = request.POST.get("newbid")
    auctionsid = request.POST.get("auctionid")
    buyer = User.objects.get(username=request.POST.get("user"))

    # Don´t let seller buy its own listing
    actualauction = Auction.objects.get(pk=auctionsid)
    if buyer == actualauction.seller:
        auctions = filter_sold_render_images("no")
        return render(request, "auctions/index.html", 
        { "auctions": auctions, "bid": Bid.objects.all(),
        "messege": "Sory, you cant´place a Bid over your own product"})
    else:
        # Try to get the Anterior Bid, if there is one
        try:
            bid = Bid.objects.get(auction_product=auctionsid)
            if int(new_bid) <= int(bid.last_bid):
                return render(request, "auctions/index.html", { "auctions": auctions, "bid": Bid.objects.all(),
                "messege": "Sory, your Bid must be bigger than the products last bid"})
            else:
                bid.current_buyer=buyer
                bid.last_bid = int(new_bid)
                bid.save()  
                return HttpResponseRedirect(reverse("listing", args=(buyer.id, auctionsid)))
        except:
            if int(new_bid) < int(actualauction.starting_bid):
                return render(request, "auctions/index.html", { "auctions": auctions, "bid": Bid.objects.all(),
                "messege": "Sory, your Bid must be iqual or bigger than the products starting price"})
            else:
                ultimatebid = Bid(auction_product=actualauction,current_buyer=buyer,last_bid=new_bid,winner=False)
                ultimatebid.save()  
            return HttpResponseRedirect(reverse("listing", args=(buyer.id, auctionsid)))

@login_required(login_url="login")
def CloseAuction(request):
    auctionsid =request.POST.get("auctionid")
    sold_auction = Auction.objects.get(pk=auctionsid)
    ultimate_bid = Bid.objects.get(auction_product=sold_auction)
    sold_auction.sold = True
    sold_auction.save()
    ultimate_bid.winner = True
    ultimate_bid.save()
    auctions = filter_sold_render_images("no")
    return render(request, "auctions/index.html", 
    { "auctions": auctions, "bid": Bid.objects.all(),
    "messege": f"You finished the auction, the winner is {ultimate_bid.current_buyer}"})
    

@login_required(login_url="login")
def WatchList(request, user_id):
    auctions = filter_sold_render_images("watchlist", user_id)
    return render(request, "auctions/WatchList.html", 
    { "auctions": auctions, "bid": Bid.objects.all()
    })

@login_required(login_url="login")
def AddToWatchList(request):
    user_name = User.objects.get(username=request.POST.get("usersname"))
    auctionsid =request.POST.get("auctionid")
    auction_id = Auction.objects.get(pk=auctionsid)
    try:
        watched_auction = Watch_list.objects.get(auction=auction_id,user=user_name.id)
        
        if watched_auction.watch:
            watched_auction.watch = False
        else:
            watched_auction.watch = True
        watched_auction.save()  
        return HttpResponseRedirect(reverse("listing", args=(user_name.id, auctionsid)))
    except:
        watchedauction = Watch_list(user=user_name,watch=True, auction=auction_id)
        watchedauction.save()      
        return HttpResponseRedirect(reverse("listing", args=(user_name.id, auctionsid)))


@login_required(login_url="login")
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/newlisting.html", {"Categories":Category.objects.all()
        })
    else:
        # Request Form
        user = request.POST.get("logeduser")
        title = request.POST.get("listing_title")
        firstprice = request.POST.get("firstbid")
        coment = request.POST.get("listingcoment")
        image = request.POST.get("imageurl")
        categories = Category.objects.all()
        choosed_category = None
        for category in categories:
            if category.category_name in request.POST:
                choosed_category = category
        new_auction = Auction(seller=User.objects.get(pk=user),product_name=title,description=coment,auction_image=image,
        starting_bid=firstprice,sold=False,category_name=choosed_category)
        new_auction.save()
        return HttpResponseRedirect(reverse("listing", args=(user, new_auction.id,)))