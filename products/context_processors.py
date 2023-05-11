from .models import category,Product
from django.db.models import Min,Max

def menu_links(request):
    links = category.objects.all()
    minMaxPrice=Product.objects.aggregate(Min('price'),Max('price'))
    return dict(links = links,minMaxPrice= minMaxPrice) 