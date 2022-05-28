from django.db import models
from django.contrib.auth.models import User
from pkg_resources import require

# redundant model
class Favourites(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    favourites = models.TextField(default = "")

# Create your models here.
class Song(models.Model):

    Language_Choice = (
              ('Hindi', 'Hindi'),
              ('English', 'English'),
          )

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=20, choices=Language_Choice, default='English')
    song_img = models.FileField(default = 'CloverBuddies.jpg')
    artist = models.TextField(default = "")

    # Collaborative Filtering
    likes = models.IntegerField(default = 0)
    likedBy = models.TextField(default = "none")
    
    # Song attributes
    valence = models.FloatField(default = 0.00)
    year = models.IntegerField(default = 2022)
    acousticness = models.FloatField(default = 0.00)
    danceability = models.FloatField(default = 0.00)
    duration_ms = models.IntegerField(default = 0)
    energy = models.FloatField(default = 0.00)
    explicit = models.IntegerField(default = 0)
    song_id = models.CharField(max_length = 200, unique = True)
    instrumentalness = models.FloatField(default = 0.00)
    key = models.IntegerField(default = 0)
    liveness = models.FloatField(default = 0.00)
    loudness = models.FloatField(default = 0.00)
    mode = models.IntegerField(default = 0)
    popularity = models.IntegerField(default = 0)
    release_date = models.CharField(max_length = 255, default = "1921")
    speechiness = models.FloatField(default = 0.00)
    tempo = models.FloatField(default = 0.00)
    
    def __str__(self): #string name in django admin view
        return "id : " + str(self.id) + " - " + self.name


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=200)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)


class Favourite(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    is_fav = models.BooleanField(default=False)


class Recent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)