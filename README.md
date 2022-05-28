# Music Recommender System

I created a Music Recommender System using Collaborative Filtering and K-Means Clustering algorithm.

## Steps to run the app
1) Create environment using following command in cmd:  
   python -m venv env
   ./env/Scripts/activate
2) Type this command to download dependencies in local machine:
   pip install -r requirements.txt
3) Make migrations:
   py manage.py makemigrations musicapp
4) Go to browser and type the following in the search bar to create the database:
   localhost:8000/fill_data/songs
5) Train the model:
   localhost:8000/train
6) Type the following command in cmd:
   python manage.py runserver
7) Open the browser in default port localhost:8000
8) Sign up first. Then click on some song and click on the favourite button. Go back to the 'AllSongs' tab, and you will see 'Recommended Songs' at the top.

## Important points to keep in mind in order to run the app:

It was my first time working on Machine learning so there will be some bugs in it. I will list down the path to follow in order to get the recommendations correctly. i intend to work on this project and improve all its bugs in the future once I have better knowledge.

1) You must click on atleast one song first so that it goes into the Last played Songs list and the code will work only then.
2) For recommendations to generate under the 'All Songs' category, another user must have atleast one same song favourited. Collaborative filtering has been used here. For eg: if User A has favourited the song- Gati Bali, and User B has favourited the same song as well. The algorithm will work.
3) Recommendations will take some time to load about 30 seconds, as the K-Means Clustering algorithm is slow while finding the nearest neighbours.

## Algorithm:

Collaborative Filtering-
  We loop through the songs that current logged in user A has favourited. We then loop through all the other users who have also favourited the same song( eg: B and C). Then we loop iterate through the list of songs favourited by user B and C and append them to a list. We sort the list based on the highest number of favourites and take the top 1 song to be used in our K-means clustering algorithm.
  
 K-Means Clustering Algorithm-
  We take the top 1 song from the Collaborative Filtering Algorithm and find the songs similar to them judging by the song attributes we gave (Eg: acousticness, etc) and return 9 recommendations. So in total top 10 recommendations are shown to the user A.
