Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

This app is connected to an API created with Python Flask connected to a PostgreSQL database for storing, querying, and creating information about artists and venues. The site is able to do the following:

* creating new venues, artists, and creating new shows.
* searching for venues and artists.
* learning more about a specific artist or venue.

NB: This is one of my projects in the Udacity Full Stack Developer Nanodegree Program

## Tech Stack (Dependencies)

### 1. Backend Dependencies
The tech stack used include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations
You can download and install the dependencies mentioned above using `pip` as:
```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```

### 2. Frontend Dependencies
The front-end part of the site was created using **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/). Bootstrap was installed using Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). After successfully installing the Node, verify the installation as shown below.
```
node -v
npm -v
```
Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:
```
npm init -y
npm install bootstrap@3
```

## Development Setup
1. **Download the project starter code locally**
```
git clone https://github.com/Timmy-id/fyyur.git
cd fyyur/ 
```

2. **Initialize and activate a virtualenv using:**
```
py -m virtualenv env
source env\Scripts\activate
```

4. **Install the dependencies:**
```
pip install -r requirements.txt
```

5. **Run the development server using windows powershell:**
```
$env:FLASK_APP=fyyur
$env:FLASK_ENV=development # enables debug mode
flask run
```

6. **Verify on the Browser**<br>
Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 

