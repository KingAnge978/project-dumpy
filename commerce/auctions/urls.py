from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category_listings, name="category_listings"),
    path("listing/<int:listing_id>/watch", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/comment", views.add_comment, name="add_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category_listings, name="category_listings"),
    path("category/create", views.create_category, name="create_category"),
    path("category/<int:category_id>/delete", views.delete_category, name="delete_category"),
]
