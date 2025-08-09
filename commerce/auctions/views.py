from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Category
from .forms import CategoryForm

def index(request):
    active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

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
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

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


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = float(request.POST["starting_bid"])
        image_url = request.POST.get("image_url", "")
        category_id = request.POST.get("category")
        
        category = None
        if category_id:
            category = Category.objects.get(pk=category_id)
        
        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            current_price=starting_bid,
            image_url=image_url,
            category=category,
            creator=request.user
        )
        listing.save()
        
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
    
    categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        "categories": categories
    })

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    in_watchlist = request.user in listing.watchers.all() if request.user.is_authenticated else False
    comments = listing.comments.all()
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "comments": comments,
        "error": None
    })

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user in listing.watchers.all():
        listing.watchers.remove(request.user)
    else:
        listing.watchers.add(request.user)
    
    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_amount = float(request.POST["bid_amount"])
    
    if bid_amount < listing.starting_bid or (listing.bids.exists() and bid_amount <= listing.bids.first().amount):
        error = "Your bid must be at least as large as the starting bid and greater than any other bids."
        comments = listing.comments.all()
        in_watchlist = request.user in listing.watchers.all()
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "in_watchlist": in_watchlist,
            "comments": comments,
            "error": error
        })
    
    bid = Bid(amount=bid_amount, bidder=request.user, listing=listing)
    bid.save()
    
    listing.current_price = bid_amount
    listing.save()
    
    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user == listing.creator and listing.active:
        if listing.bids.exists():
            listing.winner = listing.bids.first().bidder
        listing.active = False
        listing.save()
    
    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    content = request.POST["comment"]
    
    comment = Comment(content=content, author=request.user, listing=listing)
    comment.save()
    
    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

@login_required
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist
    })

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listings.filter(active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect(reverse('categories'))
    else:
        form = CategoryForm()
    return render(request, 'auctions/category_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect(reverse('categories'))
    return render(request, 'auctions/category_confirm_delete.html', {'category': category})
