# Flask Web App Tutorial Series: Step-by-Step Instructions
 

 ## Initial Setup
 

 1.  Set up a basic Flask application with routes for the home page and about page [1].
 2.  Create HTML templates for each route within a templates folder [2].
 

 ## Templates
 

 1.  **Create base template**: Establish a base layout template (`layout.html`) to maintain a consistent structure across all pages [3].
 2.  **Implement template inheritance**: Inherit the base template in other templates to avoid repetitive code and ensure a uniform design [3].
 3.  **Add navigation bar**: Include a navigation bar in the base template for easy navigation between different sections of the site [4].
 4.  **Pass data to templates**: Pass data from the Python code to the HTML templates to display dynamic content [5].
 

 ## Forms and User Input
 

 1.  **Install Flask-WTF**: Use `pip install flask-wtf` to install Flask-WTF, a library for form handling [6].
 2.  **Create form classes**: Define form classes using WTForms in a separate `forms.py` file. Include fields for registration and login [6].
 3.  **Integrate forms in routes**: Create instances of the form classes in the respective routes and pass them to the templates [7].
 4.  **Render forms in templates**: Render the forms in the HTML templates, utilizing WTForms's built-in functions to generate form fields [8].
 5.  **Validate user input**: Implement form validation to ensure that the user provides valid information [9].
 

 ## Database Setup with Flask-SQLAlchemy
 

 1.  **Install Flask-SQLAlchemy**: Use `pip install flask-sqlalchemy` to install Flask-SQLAlchemy for database integration [10].
 2.  **Configure the database**: Configure the Flask application to use a database, such as SQLite, by setting the `SQLALCHEMY_DATABASE_URI` configuration variable [10].
 3.  **Define database models**: Define database models for users and posts, specifying the structure and relationships between them [10].
 4.  **Create the database**: Create the database tables using `db.create_all()` [11].
 

 ## Package Structure
 

 1.  **Convert to a package**: Restructure the application into a package by creating an `__init__.py` file in the project directory [12].
 2.  **Organize application components**: Organize the application components into separate modules within the package [12].
 

 ## User Authentication
 

 1.  **Install Flask-Bcrypt**: Use `pip install flask-bcrypt` to install Flask-Bcrypt for password hashing [13].
 2.  **Hash passwords**: Hash user passwords before storing them in the database to protect user data [13].
 3.  **Implement user registration**: Add logic to the registration route to create new users and store them in the database [13].
 4.  **Install Flask-Login**: Use `pip install flask-login` to install Flask-Login for managing user sessions [14].
 5.  **Implement user login and logout**: Create login and logout routes to authenticate users and manage their sessions [14].
 6.  **Restrict route access**: Use the `@login_required` decorator to restrict access to certain routes to logged-in users only [14].
 

 ## User Account and Profile Picture
 

 1.  **Update account template**: Modify the template for the account page to allow users to update their information and upload a profile picture [15].
 2.  **Create account form**: Create a form for updating user information, including fields for username, email, and profile picture [16].
 3.  **Implement picture upload**: Implement functionality to allow users to upload a profile picture and store it on the server [16].
 4.  **Update user information**: Add logic to the account route to update the user's information in the database [16].
 

 ## Create, Update, and Delete Posts
 

 1.  **Create new post page**: Create a route for users to write a new post, requiring them to be logged in [17].
 2.  **Post form**: Create a `PostForm` class using Flask-WTF, including `title` (StringField), `content` (TextAreaField), and `submit` (SubmitField). DataRequired validators are added to ensure that every post has a title and content [17].
 3.  **Add posts to the database**: When a valid form is submitted, a new `Post` object is created with the title, content, and author (current user) from the form data. The post is added to the database session and committed [18].
 4.  **Display posts on the home page**: Modify the home page route to query all posts from the database and pass them to the template. Remove the dummy data. Display the author's username and post date. Display the user's profile picture with their post [18].
 5.  **Updating posts**: Create a new route for updating a specific post, requiring the user to be logged in. The route checks if the current user is the author of the post; if not, a 403 error is returned. The `PostForm` is pre-filled with the existing post data [19].
 6.  **Deleting posts**: Create a delete route, similar to the update route, which only accepts POST requests. After verifying that the current user is the author, the post is deleted from the database, and the user is redirected to the home page with a deletion message. Add a confirmation modal to ensure that the user wants to delete the post [19].
 

 ## Pagination
 

 1.  **Implement pagination**: Implement pagination to efficiently retrieve a limited number of posts per page [20].
 2.  **Sort posts**: Implement logic to sort posts by the newest or oldest entries [21].
 3.  **User-specific pages**: Create user-specific pages that display posts written by a specific user [21].
 

 ## Custom Domain Name
 

 1.  **Purchase a domain name**: Buy a domain from a domain registrar [22].
 2.  **Set name servers**: Configure the domain to use the hosting provider's name servers [22].
 3.  **Create a DNS zone**: Create a DNS zone using the DNS manager [23].
 4.  **Create DNS records**: Create DNS records for the domain [24].
 5.  **Set up reverse DNS**: Set up reverse DNS for the domain [25].
 

 ## HTTPS with Let's Encrypt
 

 1.  **SSH into your server**: Establish an SSH connection to the server [26].
 2.  **Install the Let's Encrypt client**: Install the Certbot client on the server [27].
 3.  **Obtain an SSL certificate**: Use Certbot to obtain an SSL certificate for the domain [28].
 4.  **Configure auto-renewal**: Set up automatic renewal of the SSL certificate using a cron job [29].