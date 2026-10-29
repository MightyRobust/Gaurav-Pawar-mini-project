from django.db import models

class Registration(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    SPORT_CHOICES = [
        ('cricket', 'Cricket'),
        ('football', 'Football'),
        ('volleyball', 'Volleyball'),
        ('badminton', 'Badminton'),
        ('chess', 'Chess'),
        ('kabaddi', 'Kabaddi'),
        ('carrom', 'Carrom'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    branch_sem = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sport_str = self.get_sport_display() if self.sport else "General"
        return f"{self.full_name} - {sport_str} ({self.team_name or 'Individual'})"


class ContactMessage(models.Model):
    fullname = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} ({self.email})"