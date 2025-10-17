# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

It's a simple, mobile-friendly web app that allows users to browse, add, edit, and manage art collections while exploring other artists and their works.

## User stories

### Authentication 

- As a new user, I want to create an account with a username, email, and password, so that I can join the community and explore.
- As a user, I want to log in securely before adding or editing artworks, so that only authorized users can modify the collection.
- As a user, I want to securly log out, so that others cannot access my account on a shared device.
- As a user, I want to receive clear error messages if login or signup fails so that I know what to fix. 
- As a user, I want all my user passwords to be securely hashed before being stored in MongoDb, so that user credentials are protected. 

### Interface & User Experience

- As a user, I want the website to be fully responsive and mobile friendly, so that I can comfortably browse on my phone, tablet or desktop. 
- As an artist, I want to see a confirmation message after successfully uploading art so that I know my action was completed.

### Core Features

- As an artist, I want a personal profile page that displays my banner, bio and social links, so I can create a customizable profile.
- As an artist, I want to see a clean grid of all my uploaded work on my profile page, so that visitors can browse my portfolio.
- As an artist, I want to access editing on my profile page so I can keep my details current.
- As an artist, I want to add new artworks with complete details including images, prices, and descriptions
- As an artist, I want to edit existing artwork information to keep the gallery up to date
- As an artist, I want to delete artworks that are no longer available
- As an artist, I want all artwork data to be securely stored and retrieved from MongoDb, so that information is not lost between sessions and can scale with user traffic.
- As a user, I want to "like" an artwork, so I can show appreciation for the artist's work.
- As a user, I want to post comments or ask questions on an artwork's detail page, so I can engage with the artist.
- As a user, I want to browse all artworks in the gallery so I can discover new art
- As a user, I want to search for specific artworks, artists, or styles
- As a user, I want to filter artworks by year created or artistic medium, so that I can explore specific time periods or styles.
- As a user, I want to view an artwork's process using a slider, so I can easily scrub through the creation steps.
- As a user, I want to see a preview of the process on the homepage so that I can get a glimpse before clicking. 



## Steps necessary to run the software

### 1. Clone the Repository
Use the command below to download the project to your computer:

```bash
git clone https://github.com/swe-students-fall2025/2-web-app-goodenough.git
```
### 2. Install the Dependencies
Run the following command to install necessary dependencies:

```bash
pip install -r requirements.txt
```

### 3. Create your own .env File
Copy the example environment file to your own by running the following command:

```bash
cp env.example .env
```

### 4. Run the Flask App
Start the Flask application using:

```bash
flask --app app run --debug
```
## Task boards

https://github.com/orgs/swe-students-fall2025/projects/21
