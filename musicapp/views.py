import csv
import pickle
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
from .models import *
from django.db.models import Q
from sklearn.cluster import KMeans
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
warnings.filterwarnings("ignore")


class SpotifyRecommender():
    def __init__(self, rec_data):
        # our class should understand which data to work with
        self.rec_data_ = rec_data

    # if we need to change data
    def change_data(self, rec_data):
        self.rec_data_ = rec_data

    # function which returns recommendations, we can also choose the amount of songs to be recommended
    def get_recommendations(self, song_name, amount=1):
        distances = []
        # choosing the data for our song
        print("Finding recommendations for song :", song_name)
        song = self.rec_data_[
            (self.rec_data_.name.str.lower() == song_name.lower())].head(1).values[0]
        print("song data:", song)
        # dropping the data with our song
        res_data = self.rec_data_[
            self.rec_data_.name.str.lower() != song_name.lower()]
        print("Checking status ----------------------")
        for r_song in tqdm(res_data.values):
            dist = 0
            for col in np.arange(len(res_data.columns)):
                # indices of non-numerical columns
                if not col in [3, 8, 14, 1, 16]:
                    # calculating the manhattan distances for each numerical feature
                    dist = dist + \
                        np.absolute(float(song[col]) - float(r_song[col]))
            distances.append(dist)
        print("Done")
        res_data['distance'] = distances
        # sorting our data to be ascending by 'distance' feature
        res_data = res_data.sort_values('distance')
        columns = ['artists', 'name', 'id']
        return res_data[columns][:amount].values.tolist()


def train(request):
    data = pd.read_csv("data.csv")
    print("shape :", data.shape)

    def normalize_column(col):
        max_d = data[col].max()
        min_d = data[col].min()
        data[col] = (data[col] - min_d)/(max_d - min_d)

    num_types = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    num = data.select_dtypes(include=num_types)

    for col in num.columns:
        normalize_column(col)

    km = KMeans(n_clusters=10)
    cat = km.fit_predict(num)
    data['cat'] = cat
    normalize_column('cat')

    recommender = SpotifyRecommender(data)
    print("Create recommender : )")
    print("Checking demo recommendation :",
          recommender.get_recommendations('come as you are', 10))

    pickle.dump(recommender, open("trained_model.sav", 'wb'))

    return HttpResponse("Trained !")


def fill_songs(request):
    dataset = "data.csv"

    rows = []
    with open(dataset, 'r+', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)
    print(header)
    print(rows[0])

    total = len(rows)
    counter = 0
    for row in rows:
        counter += 1
        print("Creating row:", counter, " of", total, end="")
        row[3] = ' '.join(row[3].strip('][').split(', '))
        try:
            new_song = Song.objects.create(
                valence=row[0],
                year=row[1],
                acousticness=row[2],
                artist=row[3],
                danceability=row[4],
                duration_ms=row[5],
                energy=row[6],
                explicit=row[7],
                song_id=row[8],
                instrumentalness=row[9],
                key=row[10],
                liveness=row[11],
                loudness=row[12],
                mode=row[13],
                name=row[14],
                popularity=row[15],
                release_date=row[16],
                speechiness=row[17],
                tempo=row[18]
            )
            new_song.save()
            print(new_song)
        except Exception as error:
            print(error)

    return HttpResponse("Fill was successfull")

# Create your views here.


def index(request):

    # Display recent songs
    if not request.user.is_anonymous:
        recent = list(Recent.objects.filter(
            user=request.user).values('song_id').order_by('-id'))
        recent_id = [each['song_id'] for each in recent][:5]
        recent_songs_unsorted = Song.objects.filter(
            id__in=recent_id, recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(id=id))
    else:
        recent = None
        recent_songs = None

    first_time = False
    # Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(
            user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(id=last_played_id)
        else:
            first_time = True
            last_played_song = Song.objects.all().first()

    else:
        first_time = True
        last_played_song = Song.objects.all().first()

    # Display all songs
    songs = Song.objects.all()

    # Display few songs on home page
    songs_all = list(Song.objects.all().values('id').order_by('?'))
    sliced_ids = [each['id'] for each in songs_all][:5]
    indexpage_songs = Song.objects.filter(id__in=sliced_ids)

    # Display Hindi Songs
    songs_hindi = list(Song.objects.filter(language='Hindi').values('id'))
    sliced_ids = [each['id'] for each in songs_hindi][:5]
    indexpage_hindi_songs = Song.objects.filter(id__in=sliced_ids)

    # Display English Songs
    songs_english = list(Song.objects.filter(language='English').values('id'))
    sliced_ids = [each['id'] for each in songs_english][:5]
    indexpage_english_songs = Song.objects.filter(id__in=sliced_ids)

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = songs.filter(
            Q(name__icontains=search_query)).distinct()
        context = {'all_songs': filtered_songs,
                   'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/index.html', context)

    context = {
        'all_songs': indexpage_songs,
        'recent_songs': recent_songs,
        'hindi_songs': indexpage_hindi_songs,
        'english_songs': indexpage_english_songs,
        'last_played': last_played_song,
        'first_time': first_time,
        'query_search': False,
    }
    return render(request, 'musicapp/index.html', context=context)


def hindi_songs(request):

    hindi_songs = Song.objects.filter(language='Hindi')

    # Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.all().first()

    query = request.GET.get('q')

    if query:
        hindi_songs = Song.objects.filter(Q(name__icontains=query)).distinct()
        context = {'hindi_songs': hindi_songs}
        return render(request, 'musicapp/hindi_songs.html', context)

    context = {'hindi_songs': hindi_songs, 'last_played': last_played_song}
    return render(request, 'musicapp/hindi_songs.html', context=context)


def english_songs(request):

    english_songs = Song.objects.filter(language='English')

    # Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.all().first()

    query = request.GET.get('q')

    if query:
        english_songs = Song.objects.filter(
            Q(name__icontains=query)).distinct()
        context = {'english_songs': english_songs}
        return render(request, 'musicapp/english_songs.html', context)

    context = {'english_songs': english_songs, 'last_played': last_played_song}
    return render(request, 'musicapp/english_songs.html', context=context)


@login_required(login_url='login')
def play_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()
    return redirect('all_songs')


@login_required(login_url='login')
def play_song_index(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()
    return redirect('index')


@login_required(login_url='login')
def play_recent_song(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()
    return redirect('recent')


def collaborative_filtering(username):
    favourites = Favourite.objects.filter(user=username, is_fav=True)
    songs = [favourite.song.likedBy for favourite in favourites]
    friend_users = set()
    for song_likes in songs:
        song_likes = song_likes.split(" | ")
        if song_likes is not None and len(song_likes) > 0:
            for user_id in song_likes:
                if user_id == "none":
                    continue
                friend_users.add(int(user_id))
    try:
        friend_users.remove(username.id)
    except Exception as error:
        print(error)
    print(friend_users)

    friend_users = list(friend_users)
    all_favourites = set()
    for friend in friend_users:
        try:
            friend_user = User.objects.get(id=friend)
        except Exception as error:
            print(error)

        friend_user_favourites = Favourite.objects.filter(
            user=friend_user, is_fav=True)
        for friend_user_favourite in friend_user_favourites:
            all_favourites.add((friend_user_favourite.song,
                               friend_user_favourite.song.likes))
    print(all_favourites)
    return list(all_favourites)


def all_songs(request):
    songs = Song.objects.all()

    user = User.objects.get(username=request.user)
    cf_results = collaborative_filtering(user)

    sorted(cf_results, key=lambda x: x[1], reverse=True)[5:]
    print("sorted results : ", cf_results)

    
    print("Inside the all_songs function")
    recommender = pickle.load(open("trained_model.sav", 'rb'))
    print("recommender : ", recommender)
    recommendations = set()
    for cf_song in cf_results[:1]:
        cf_song_recommendations = recommender.get_recommendations(
            cf_song[0].name, 10)
        for recommended_song in cf_song_recommendations:
            print(recommended_song[2])
            try:
                rsong = Song.objects.get(song_id=recommended_song[2])
                recommendations.add((rsong, rsong.likes))
            except Exception as error:
                print(error)
        print(cf_song_recommendations)
    recommendations = list(recommendations)
    k_means_results = sorted(
        recommendations, key=lambda x: x[1], reverse=True)[:9]

    recommended = set()

    for cf_result in cf_results:
        if len(recommended) > 10:
            break
        recommended.add(cf_result[0])

    for k_means_result in k_means_results:
        if len(recommended) > 10:
            break
        recommended.add(k_means_result[0])

    recommended = list(recommended)
    print("Number of songs recommended :", len(recommended))

    first_time = False
    # Last played song
    if not request.user.is_anonymous:
        last_played_list = list(Recent.objects.filter(
            user=request.user).values('song_id').order_by('-id'))
        if last_played_list:
            last_played_id = last_played_list[0]['song_id']
            last_played_song = Song.objects.get(id=last_played_id)
    else:
        first_time = True
        last_played_song = Song.objects.all().first()

    # apply search filters
    qs_artists = Song.objects.values_list('artist').all()
    s_list = [s.split(',') for artist in qs_artists for s in artist]
    all_artists = sorted(
        list(set([s.strip() for artist in s_list for s in artist])))
    qs_languages = Song.objects.values_list('language').all()
    all_languages = sorted(
        list(set([l.strip() for lang in qs_languages for l in lang])))

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        search_artist = request.GET.get('artist') or ''
        search_language = request.GET.get('languages') or ''
        filtered_songs = songs.filter(Q(name__icontains=search_query)).filter(
            Q(language__icontains=search_language)).filter(Q(artist__icontains=search_artist)).distinct()
        filtered_songs = filtered_songs[:20]
        context = {
            'songs': filtered_songs,
            'last_played': last_played_song,
            'all_artists': all_artists,
            'all_languages': all_languages,
            'query_search': True,
        }
        return render(request, 'musicapp/all_songs.html', context)

    context = {
        'songs': songs[:20],
        'last_played': last_played_song,
        'first_time': first_time,
        'recommended_songs_cf': recommended[:10],
        'all_artists': all_artists,
        'all_languages': all_languages,
        'query_search': False,
    }
    return render(request, 'musicapp/all_songs.html', context=context)


def recent(request):

    # Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.all().first()
        print("Last played song is : ", last_played_song)

    # Display recent songs
    recent = list(Recent.objects.filter(
        user=request.user).values('song_id').order_by('-id'))
    if recent and not request.user.is_anonymous:
        recent_id = [each['song_id'] for each in recent]
        recent_songs_unsorted = Song.objects.filter(
            id__in=recent_id, recent__user=request.user)
        recent_songs = list()
        for id in recent_id:
            recent_songs.append(recent_songs_unsorted.get(id=id))
    else:
        recent_songs = None

    if len(request.GET) > 0:
        search_query = request.GET.get('q')
        filtered_songs = recent_songs_unsorted.filter(
            Q(name__icontains=search_query)).distinct()
        context = {'recent_songs': filtered_songs,
                   'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/recent.html', context)

    context = {'recent_songs': recent_songs,
               'last_played': last_played_song, 'query_search': False}
    return render(request, 'musicapp/recent.html', context=context)


@login_required(login_url='login')
def detail(request, song_id):
    songs = Song.objects.filter(id=song_id).first()

    # Add data to recent database
    if list(Recent.objects.filter(song=songs, user=request.user).values()):
        data = Recent.objects.filter(song=songs, user=request.user)
        data.delete()
    data = Recent(song=songs, user=request.user)
    data.save()

    # Last played song
    last_played_list = list(Recent.objects.values('song_id').order_by('-id'))
    if last_played_list:
        last_played_id = last_played_list[0]['song_id']
        last_played_song = Song.objects.get(id=last_played_id)
    else:
        last_played_song = Song.objects.all().first()

    playlists = Playlist.objects.filter(
        user=request.user).values('playlist_name').distinct
    is_favourite = Favourite.objects.filter(
        user=request.user).filter(song=song_id).values('is_fav')

    if request.method == "POST":
        if 'playlist' in request.POST:
            playlist_name = request.POST["playlist"]
            q = Playlist(user=request.user, song=songs,
                         playlist_name=playlist_name)
            q.save()
            messages.success(request, "Song added to playlist!")

        elif 'add-fav' in request.POST:

            is_fav = True
            query = Favourite(user=request.user, song=songs, is_fav=is_fav)
            print(f'query: {query}')
            query.save()

            if songs.likedBy == "none":
                songs.likedBy = str(request.user.id)
            else:
                songs.likedBy = songs.likedBy + " | " + str(request.user.id)
            songs.likes += 1
            songs.save()

            messages.success(request, "Added to favorite!")
            return redirect('detail', song_id=song_id)

        elif 'rm-fav' in request.POST:
            is_fav = True
            query = Favourite.objects.filter(
                user=request.user, song=songs, is_fav=is_fav)
            print(f'user: {request.user}')
            print(f'song: {songs.id} - {songs}')
            print(f'query: {query}')
            query.delete()

            string = songs.likedBy
            temp = [int(x.strip()) for x in string.split('|')]
            try:
                temp.pop(temp.index(request.user.id))
            except:
                print("Seems no user", request.user.id, " was present")
            newLikedBy = ' | '.join([str(x) for x in temp])
            if len(temp) == 0:
                songs.likedBy = "none"
            else:
                songs.likedBy = newLikedBy
            songs.likes -= 1
            songs.save()

            messages.success(request, "Removed from favorite!")
            return redirect('detail', song_id=song_id)

    context = {'songs': songs, 'playlists': playlists,
               'is_favourite': is_favourite, 'last_played': last_played_song}
    return render(request, 'musicapp/detail.html', context=context)


def mymusic(request):
    return render(request, 'musicapp/mymusic.html')


def playlist(request):
    playlists = Playlist.objects.filter(
        user=request.user).values('playlist_name').distinct
    context = {'playlists': playlists}
    return render(request, 'musicapp/playlist.html', context=context)


def playlist_songs(request, playlist_name):
    songs = Song.objects.filter(
        playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        playlist_song = Playlist.objects.filter(
            playlist_name=playlist_name, song__id=song_id, user=request.user)
        playlist_song.delete()
        messages.success(request, "Song removed from playlist!")

    context = {'playlist_name': playlist_name, 'songs': songs}

    return render(request, 'musicapp/playlist_songs.html', context=context)


def favourite(request):
    songs = Song.objects.filter(
        favourite__user=request.user, favourite__is_fav=True).distinct()
    print(f'songs: {songs}')

    if request.method == "POST":
        song_id = list(request.POST.keys())[1]
        favourite_song = Favourite.objects.filter(
            user=request.user, song__id=song_id, is_fav=True)
        favourite_song.delete()

        given_song = Song.objects.get(id=int(song_id))
        string = given_song.likedBy
        temp = [int(x.strip()) for x in string.split('|')]
        try:
            temp.pop(temp.index(request.user.id))
        except:
            print("Seems no user", request.user.id, " was present")
        newLikedBy = ' | '.join([str(x) for x in temp])
        if len(temp) == 0:
            given_song.likedBy = "none"
        else:
            given_song.likedBy = newLikedBy
        given_song.likes -= 1
        print(newLikedBy)
        given_song.save()

        messages.success(request, "Removed from favourite!")
    context = {'songs': songs}
    return render(request, 'musicapp/favourite.html', context=context)
