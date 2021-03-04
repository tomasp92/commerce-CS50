from django.contrib.auth.models import AbstractUser
from django.db import models
from os.path import join
import os
from commerce.settings import BASE_DIR

def images_path():
    return os.path.join(BASE_DIR,'auctions', 'static', 'auctions', 'media')

class User(AbstractUser):
    pass

class Category(models.Model):
    category_name =  models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category_name}"

class Auction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions_owned")
    product_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    auction_image = models.FilePathField(path=images_path, blank=True, null=True)
    starting_bid = models.IntegerField()
    sold = models.BooleanField()
    category_name = models.ForeignKey(Category, related_name="auctions_with_category", on_delete=models.SET_NULL, null= True)

    def __str__(self):
        return f"{self.product_name}"

class Bid(models.Model):
    auction_product = models.ForeignKey(Auction, on_delete=models.CASCADE)
    current_buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    last_bid = models.IntegerField()
    winner = models.BooleanField()

class Coment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coments_made_by")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_coments")
    text = models.CharField(max_length=500)
    
class Watch_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, blank=True, null=True, on_delete=models.CASCADE)
    watch = models.BooleanField(default=False)
