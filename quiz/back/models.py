from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    REQUIRED_FIELDS = ['email']


# class User(AbstractUser):
#     email = models.EmailField(unique=True)  # Use email as the unique identifier

#     USERNAME_FIELD = 'email'  # Set email as the unique identifier
#     REQUIRED_FIELDS = []  # Remove username and only require email

#     def __str__(self):
#         return self.email
    

class Quiz(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ])

    def __str__(self):
        return self.text


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    feedback = models.JSONField()  # Requires Django 3.1+
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"