from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="createlisting"),
    path("listing/<str:user_id>/<int:auction_id>", views.listing, name="listing"),
    path("listing/<str:category>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("addcoment", views.addcoment, name="addcoment"),
    path("NewBid", views.NewBid, name="NewBid"),
    path("CloseAuction", views.CloseAuction, name="CloseAuction"),
    path("AddToWatch_List", views.AddToWatchList, name="AddToWatchList"),
    path("Watch_List/<int:user_id>", views.WatchList, name="WatchList"),
]
