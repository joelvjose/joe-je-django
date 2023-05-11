from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

# Create your models here.

class category(models.Model):
    cat_name = models.CharField(max_length=50 , unique=True)
    slug = models.CharField(max_length=100 , null=True, blank= True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.cat_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.cat_name)
        return super().save(*args, **kwargs)
    
    def get_url(self):
        return reverse('joejee:product_by_category',args=[self.slug])
    
class Product(models.Model):
    product_name  =models.CharField(max_length=200, unique=True)
    slug          =models.CharField(max_length=200, null=True, blank= True)
    description   =models.TextField(max_length=500, blank=True)
    price         =models.IntegerField()
    stock         =models.IntegerField()
    image         =models.ImageField(upload_to='photos/product')
    is_available  =models.BooleanField(default=True)
    category      =models.ForeignKey(category,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product_name
    
    def get_url(self):
        return reverse('joejee:product_detail',args=[self.category.slug,self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        return super().save(*args, **kwargs)
    
class Images(models.Model):
    product       = models.ForeignKey(Product,on_delete=models.CASCADE)
    images         = models.ImageField(upload_to='photos/product')
    
    def __str__(self):
        return self.product.name

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active = True)
    
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active = True)
    
    
variation_category_choises = (
    ('color','color'),
    ('size','size'),
)    

class Variation(models.Model):
    product             = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category  = models.CharField(max_length=100,choices=variation_category_choises)
    variation_value     = models.CharField(max_length=100)
    price               = models.IntegerField()
    stock               = models.IntegerField()
    
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value
    

class Coupon(models.Model):
    code    = models.CharField(max_length=50,unique=True)
    discount= models.PositiveIntegerField()
    min_amount  = models.IntegerField()
    active  = models.BooleanField(default=True)
    active_date = models.DateField()
    expiry_date = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code