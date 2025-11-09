# Uncomment the following imports before adding the Model code
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class CarMake(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    # FIXED: Explicitly return str (E0307 Fix)
    def __str__(self):
        return str(self.name)

class CarModel(models.Model):
    dealer_id = models.IntegerField(default=0)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    # Choices for the car type
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    TRUCK = 'Truck'
    HATCHBACK = 'Hatchback'
    TYPE_CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (TRUCK, 'Truck'),
        (HATCHBACK, 'Hatchback'),
    ]
    car_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=SEDAN)
    
    # Year field with validators
    year = models.IntegerField(
        validators=[MinValueValidator(2015), MaxValueValidator(2023)]
    )
    
    # FIXED: Explicitly return str (E0307 Fix)
    def __str__(self):
        return str(f"{self.make.name} {self.name} ({self.year})")

# Ensure one blank line is at the end of the file.