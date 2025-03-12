from django.db import models
from django.contrib.auth.models import User

class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    experience = models.IntegerField(default=0, blank=True, null=True)  # Experience in years

    def __str__(self):
        return self.user.username

class TrainerData(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    achievements = models.IntegerField(default=0)
    classes_scheduled = models.IntegerField(default=0)
    classes_taken = models.IntegerField(default=0)
    workshops = models.IntegerField(default=0)
    students_participated = models.IntegerField(default=0)
    students_won = models.IntegerField(default=0)
    course_referrals = models.BooleanField(default=False)
    date_submitted = models.DateTimeField(auto_now_add=True)
    
    score = models.FloatField(default=0, editable=False)  # Auto-calculated field

    def calculate_score(self):
        score = 0

        # Achievements Scoring
        if self.achievements > 6:
            score += 10
        elif 5 <= self.achievements <= 6:
            score += 6
        elif 3 <= self.achievements <= 4:
            score += 4
        elif 1 <= self.achievements <= 2:
            score += 2

        # Class Performance
        if self.classes_scheduled > 0:
            score += (self.classes_taken / self.classes_scheduled) * 10

        # Workshops Scoring
        if self.workshops > 6:
            score += 10
        elif 5 <= self.workshops <= 6:
            score += 6
        elif 3 <= self.workshops <= 4:
            score += 4
        elif 1 <= self.workshops <= 2:
            score += 2

        # Student Participation
        if self.students_participated > 40:
            score += 30
        elif 31 <= self.students_participated <= 40:
            score += 25
        elif 21 <= self.students_participated <= 30:
            score += 20
        elif 11 <= self.students_participated <= 20:
            score += 15
        elif self.students_participated > 0:
            score += 10

        # Student Wins
        if self.students_won > 40:
            score += 25
        elif 31 <= self.students_won <= 40:
            score += 20
        elif 21 <= self.students_won <= 30:
            score += 15
        elif 11 <= self.students_won <= 20:
            score += 10
        elif self.students_won > 0:
            score += 10

        # Course Referrals Bonus
        if self.course_referrals:
            score += 15

        return round(score, 2)  # Return rounded score

    def save(self, *args, **kwargs):
        self.score = self.calculate_score()  # Auto-update score before saving
        super().save(*args, **kwargs)

    @property
    def rank_category(self):
        """Categorize trainer based on score"""
        if self.score > 80:
            return "Top Performer"
        elif 50 <= self.score <= 80:
            return "Good Performer"
        elif 20 <= self.score < 50:
            return "Average Performer"
        else:
            return "Underperformer"

    def __str__(self):
        return f"{self.trainer.user.username} - Score: {self.score} - Rank: {self.rank_category}"

class Feedback(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # Rating from 1 to 5
    comment = models.TextField(blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.trainer.user.username} - Rating: {self.rating}"
