# CS50 Final Project - BabyLove

#### Video Demo:  https://youtu.be/gauUkjV65qE

BabyLove is a web app using Flask that allows you to track your baby’s key activities, when you feed them, when they sleep, and how often you have to change their nappy. It provides valuable insight into these key matrices for you baby and helps parents plan their day around their baby's rhythms. It's also a great way to keep an eye on these key metrics to make sure that they are getting adequate amounts of each, and can help warn the parents of more significant issues.

## Getting Started

This web app is based around Flask, so it’s important to make sure that you have it installed, along with Python3 and Flask Session. Once you have these installed it's simply a case of making sure that each file stays in its present directory and typing "flask run" while in its route. If running on your home system go to http://127.0.0.1:5000/ to view the app, or you can deploy it to a web server and run it from your own URL.

### Prerequisites

As previously mentioned you need to have Flask, Flask Session and Python3 installed. You can install these on Linux or through WSL using the pip command, for example:

> pip install flask

### Files

## app.py

This is the core Flask file. It contains all the different app routes and configures the app. The routes are as follows:

# index

This first route just checks if the user if logged in, and directs them to the appropriate page.

# register

This route allows the user to sign up for a new account. Their sing in password is measured with a couple of checks to make it a little more secure, and then user data is inputted into a database table of users.

# login

This login route is taken from the week 9 pset - finance. All credit to the staff at CS50. It allows the user to login, but has been adapted slightly to use cookies rather than soring the data on the user’s computer.

#  add

This route allows the user to add a baby. It runs through a series of checks to make sure the needed data is supplied, then updates this data to two different tables on the database. One table holds the data of the baby, the other users 2 foreign keys to link the baby to the current user. If the user supplies a picture, this picture is saved to the babypics folder in the img folder in static and a link is saved in the database, but this is not essential to sign-up. Multiple babies per user are supported.

# track

This route directs the user to the appropriate tracking page for the baby and activity the want to track.

# activity

The activity route allows the user to track when they fed their baby, if their baby slept, or if their baby needed their nappy changed. It lets them time various activity using a stopwatch, or directly collects users data for other activities. This data is stored in a table in the database that keeps track of all activities along with a date and time stamp.

# home

This route parses all the data from the database to show an overview of the day's activities. It defaults to the current day and the first baby, but the user can cycle through all days with tracked activities and all the babies linked to their account.

## helpers.py

This file contains two functions, the login_required function from finance, and an allowed_file function copied from the Flask documentation.

## babylove.db

This is the database that stores all the data for this web app. IT's broken up into four tables, two tables with primary keys - users and babies, a table that links these two together, and a final table that stores all the activity data and links it to each baby.

## templates

This directory stores all the HTML files to be rendered by the flask app. They all use layout.html as a base to keep the style consistent. I used the agency bootstrap template from startbootstrap.com to base my website on, and made adaptations along the way.

## static

This directory contains the stylesheet for the app, as well as a JavaScript file to help the navbar more responsive. It also contains an img folder that has images used by the app, as well as a folder where images uploaded by the user are stored. For the contact me form on the home page I used a template from 1000forms.com that runs through their servers.

### Design choices

While there are a whole lot of different activities that you can track with your baby, I distilled it down to the key ones that I have been using as a father. I didn't want the parameters of the project to get out of hand. I took a while to think about how I wanted to database set up, and after looking at the IMDB database from the movies pset I settled on using an extra table to link the parents and babies together. The overall look and color scheme were taken from a bootstrap template, but I made a few changes including making sure the navbar was always available for use.

## Authors

Wai-San Peter Lee

## Acknowledgments

I want to thank all of the people on stack overflow for their help, not just on the questions I personally asked, but also questions that others asked that led me to the solutions that I was looking for.

David Malen, Doug Lloyd, Brian Yu, and all of the people on CS50, this wouldn't have been possible without your excellent teaching and guidance.

The template makers at startbootstrap.com

1000forms.com for their contact me form template

