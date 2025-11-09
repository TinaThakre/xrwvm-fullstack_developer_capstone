"""
Django models for CarMake and CarModel.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    """
    Car manufacturer model.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        """
        String representation for admin and shell.
        """
        return str(self.name)


class CarModel(models.Model):
    """
    Car model associated with a CarMake and a dealer.
    """

    dealer_id = models.IntegerField(default=0)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    # Choices for the car type
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    TRUCK = "Truck"
    HATCHBACK = "Hatchback"

    TYPE_CHOICES = [
        (SEDAN, "Sedan"),
        (SUV, "SUV"),
        (WAGON, "Wagon"),
        (TRUCK, "Truck"),
        (HATCHBACK, "Hatchback"),
    ]

    car_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=SEDAN,
    )

    # Year field with validators
    year = models.IntegerField(
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023),
        ],
    )

    def __str__(self):
        """
        String representation including make, model and year.
        """
        return f"{self.make.name} {self.name} ({self.year})"

