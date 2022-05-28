# Music Recommender System

I created a basic Music Recommender System using Collaborative Filtering and K-Means Clustering algorithm.

![image](https://user-images.githubusercontent.com/75472177/170838119-01a2388f-769b-4f46-a689-d6f9a825ebee.png)


## Steps to run the app

1) Create environment using following command in cmd:  

   `python -m venv env
   ./env/Scripts/activate`
   
2) Type this command to download dependencies in local machine:

   `pip install -r requirements.txt`
   
3) Make migrations:

   `py manage.py makemigrations musicapp`
   
4) Go to browser and type the following in the search bar to create the database:

  ` localhost:8000/fill_data/songs`
   
5) Train the model:

   `localhost:8000/train`
   
6) Type the following command in cmd:

   `python manage.py runserver`
   
7) Open the browser in default port localhost:8000

9) Sign up first. Then click on some song and click on the favourite button. Go back to the 'AllSongs' tab, and you will see 'Recommended Songs' at the top.

## Important points to keep in mind in order to run the app:

It was my first time using Machine learning so there will be some bugs in it. I will list down the path to follow in order to get the recommendations correctly. I intend to work on this project and improve all its bugs in the future once I have better knowledge.


1) You must click on atleast one song first so that it goes into the 'Last played Songs' list and the code will work only then.
2) For recommendations to generate under the 'All Songs' category, another user must have atleast one same song favourited. Collaborative filtering has been used here. For eg: if User A has favourited the song- 'Levitating', and User B has favourited the same song as well. The algorithm will work.
3) Recommendations will take some time to load about 30 seconds, as the K-Means Clustering algorithm is slow while finding the nearest neighbours.


## Algorithm:


  We iterate through the songs that the current logged in user A has favourited. We then iterate through all the other users who have also favourited the same song( eg: B and C). Then we iterate through the list of songs favourited by user B and C and append them to a list. We sort the list based on the highest number of favourites and take the top 1 song to be used in our K-means clustering algorithm.
 
 
  We take the top 1 song from the Collaborative Filtering Algorithm, find other songs similar to it using K-Means Algorithm and return 9 recommendations. So in total top 10 recommendations are shown to the user A.
