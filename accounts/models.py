from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import uuid

import json

class User(AbstractUser):
    email=models.EmailField(unique=True)
    verified_at = models.CharField(max_length=200,default='False')
    role =models.CharField(max_length=200,default='user')
    status = models.CharField(max_length=20, default='1')
    updated_at = models.CharField(max_length=200,default=datetime.utcnow())
    created_at = models.CharField(max_length=200,default=datetime.utcnow())
    remember_token=models.CharField(max_length=200,default='False')
    phone_no=models.CharField(max_length=200,null=True)
    activation_date=models.CharField(max_length=200,default='N/A')
    class Meta:
        db_table='users'


class Symbols(models.Model):
    symbol = models.CharField(max_length=200)
    status = models.CharField(max_length=100,default='1')
    class Meta:
        db_table = 'symbols'

class PortfolioSettings(models.Model):
    interval = models.CharField(max_length=100)
    symbol = models.CharField(max_length = 100)
    indicators = models.TextField()
    class Meta:
        db_table = 'portfolio_settings'


class OverView(models.Model):
    net_profit = models.CharField(max_length=200)
    total_closed_trades = models.CharField(max_length=200)
    percent_profitable = models.CharField(max_length=200)
    profit_factor = models.CharField(max_length=200)
    max_dropdown = models.CharField(max_length=200)
    avg_trades = models.CharField(max_length=200)
    gross_profit = models.CharField(max_length=200)
    gross_loss = models.CharField(max_length=200)
    buy_hold = models.CharField(max_length=200)
    avg_winning_trades = models.CharField(max_length=200)
    avg_lossing_trades = models.CharField(max_length=200)
    total_open_trades = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    class Meta:
        db_table = 'overview'



class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    class Meta:
        db_table = 'stock'
    def __str__(self):
        return f"{self.ticker} - {self.name}"




class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    note = models.TextField(blank=True, null=True)  # Optional notes about the transaction
    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.stock.ticker} ({self.quantity})"
    @property
    def total_value(self):
        return self.quantity * self.price



class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Current quantity of stocks
    average_price = models.DecimalField(max_digits=10, decimal_places=2)  # Average buy price
    
    def __str__(self):
        return f"{self.stock.ticker} - {self.quantity} shares"



class MultiScreen(models.Model):
    symbol = models.CharField(max_length= 200)
    interval = models.CharField(max_length = 200)

    class Meta:
        db_table="multi_screen"




        
