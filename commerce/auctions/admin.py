from django.contrib import admin
from. models import User, Auction, Bid, Coment, Category, Watch_list

# Register your models here.
admin.site.register(User)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Coment)
admin.site.register(Category)
admin.site.register(Watch_list)