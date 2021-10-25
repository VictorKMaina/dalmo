from types import LambdaType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from django.utils import timezone

date_format = '%Y-%m-%d'

# Extend from default user model.
class User(AbstractUser):
    pass

    def __str__(self):
        return self.username

class Moment(models.Model):
    feeling = models.CharField(max_length=50)
    cause = models.CharField(max_length=300)
    date_added = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moments')

    def save(self, *args, **kwargs):
        """Overriding default save method to save date and time instance is created."""
        if not self.id:
            self.date_added = timezone.localtime() - timezone.timedelta(days=7)
            self.feeling = self.feeling.lower()
        return super(Moment, self).save(*args, *kwargs)

    def __str__(self):
        return f"Moment {self.id}: {self.feeling}"

    @property
    def count_feeling(self):
        """Returns number of moments with the same feeling as instance"""
        cls = Moment
        return cls.objects.filter(feeling = self.feeling).count()

    @classmethod
    def date_range(cls, from_date, to_date):
        """Return list of moments within a given date range"""
        from_date = timezone.localtime().strptime(from_date, date_format)
        to_date = timezone.localtime().strptime(to_date, date_format)
        moments = cls.objects.filter(date_added__date__range=[from_date, to_date]).all()
        return moments

    def from_same_date(self):
        """Return other moments from the same date as instance"""
        cls = self.__class__
        moments = {"date":self.date_added.date(), "moments":[m for m in cls.objects.filter(date_added__date = self.date_added.date()).all()]}
        return moments

    @classmethod
    def sort_by_date(cls, from_date, to_date, moments=None):
        """Return dictionary of moments sorted by date"""
        moments = moments if moments else cls.date_range(from_date, to_date)
        dates = [d for d in {m.date_added.date() for m in moments}]
        dates.sort(reverse=True)
        return [{"date":d, "moments":moments.filter(date_added__date=d)} for d in dates]


    @classmethod
    def count_emotions(cls, from_date, to_date):
        """Return how many times each emotion is saved"""
        moments = list(cls.date_range(from_date, to_date)) 
        feeling_counts = [dict(feeling_count) for feeling_count in {tuple(feeling.items()) for feeling in [{"emotion":moment.feeling, "count":moment.count_feeling} for moment in moments]}]
        return feeling_counts

class Entry(models.Model):
    class DayRating(models.IntegerChoices):
        """Integer choices for daily datings"""
        VERY_GOOD = 5, ('really good')
        GOOD = 4, ('good')
        NEUTRAL = 3, ('neutral')
        BAD = 2, ('bad')
        VERY_BAD = 1, ('really bad')

    class TidinessRating(models.IntegerChoices):
        """Integer choices for tidiness datings"""
        VERY_TIDY = 5, ('really tidy')
        TIDY = 4, ('tidy')
        NEUTRAL = 3, ('neutral')
        UNTIDY = 2, ('untidy')
        VERY_UNTIDY = 1, ('really untidy')

    rating = models.PositiveIntegerField(choices=DayRating.choices)
    sleep_time = models.DateTimeField()
    wake_time = models.DateTimeField()
    meals_amount = models.PositiveIntegerField()
    snacks = models.BooleanField(default=False)
    water_amount = models.PositiveIntegerField()
    tidiness_rating = models.PositiveIntegerField(choices=TidinessRating.choices)
    date_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')

    class Meta:
        verbose_name_plural = 'Entries'

    def save(self, *args, **kwargs):
        """Overriding default save method to save date and time instance is created."""
        if not self.id:
            self.date_added = timezone.localtime() - timezone.timedelta(days=7)
        return super(Entry, self).save(*args, *kwargs)

    def __str__(self):
        return f"Entry {self.id}: {self.date_added.strftime('%d %b %Y')}"

    @property
    def moments_from_this_day(self):
        """Returns all Moment instances from the same date as Entry instance."""
        moments = Moment.objects.filter(date_added__date = self.date_added.date()).all()
        return moments

    @property
    def sleep_duration(self):
        """Calculates sleep duration based on sleep and wake up times and returns value in seconds"""
        sleep_duration = self.wake_time - self.sleep_time
        return sleep_duration.seconds

    @classmethod
    def date_range(cls, from_date, to_date):
        """Return list of entries within a given date range"""
        from_date = timezone.datetime.strptime(from_date, date_format)
        to_date = timezone.datetime.strptime(to_date, date_format)
        entries = cls.objects.filter(
            date_added__date__gte=from_date.date(),
            date_added__date__lte=to_date.date()).all()
        return entries

    @classmethod
    def average_rating(cls, from_date, to_date):
        """Return average daily rating of entries in date range"""
        entries = cls.date_range(from_date, to_date)
        if entries:
            average_rating = sum([entry.rating for entry in entries]) / len(entries)
            return cls.DayRating(round(average_rating))

    @classmethod
    def average_sleep_duration(cls, from_date, to_date):
        """Return average sleep duration of entries in date range"""
        entries = cls.date_range(from_date, to_date)
        if entries:
            return round(sum([e.sleep_duration for e in entries]) / len(entries))

    @classmethod
    def average_meals_amount(cls, from_date, to_date):
        """Return average number of meals had per day in given time period"""
        entries = cls.date_range(from_date, to_date)
        if entries:
            return round(sum([e.meals_amount for e in entries]) / len(entries))

    @classmethod
    def average_water_amount(cls, from_date, to_date):
        """Return average number of water glasses had per day in given time period"""
        entries = cls.date_range(from_date, to_date)
        if entries:
            return round(sum([e.water_amount for e in entries]) / len(entries))

    @classmethod
    def average_tidiness_rating(cls, from_date, to_date):
        """Return average tidiness rating of entries in date range"""
        entries = cls.date_range(from_date, to_date)
        if entries:
            average_tidiness = sum([entry.tidiness_rating for entry in entries]) / len(entries)
            return cls.DayRating(round(average_tidiness))
