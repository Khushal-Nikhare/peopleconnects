PeopleConnects

PeopleConnects is a simple social media application built with Python, FastAPI, and MongoDB. It allows users to create accounts, share posts with text and images, and interact with each other's content through likes and comments.

## Features

*   **User Authentication:**
    *   User signup and login
    *   Session management with cookies
*   **Posts:**
    *   Create, edit, and delete posts
    *   Upload images with posts
*   **Social Interaction:**
    *   Like and unlike posts
    *   Comment on posts
*   **User Profiles:**
    *   View user profiles with their posts
*   **Real-time Feed:**
    *   See a live feed of posts from all users

## Technologies Used

*   **Backend:**
    *   [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.
    *   [MongoDB](https://www.mongodb.com/): A NoSQL document-oriented database.
    *   [Uvicorn](https://www.uvicorn.org/): An ASGI server for Python.
*   **Frontend:**
    *   [Jinja2](https://jinja.palletsprojects.com/): A modern and designer-friendly templating language for Python.
    *   [Bootstrap](https://getbootstrap.com/): A popular CSS framework for developing responsive and mobile-first websites.
    *   [Font Awesome](https://fontawesome.com/): A popular icon set and toolkit.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Khushal-Nikhare/peopleconnects.git
    PeopleConnects
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Make sure you have MongoDB installed and running.**

4.  **Run the application:**

    ```bash
    python -m uvicorn main:app --reload
    ```

5.  **Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000)**

## File Structure

```
.
├── .gitattributes
├── .gitignore
├── main.py
├── README.md
├── static
│   └── style.css
├── templates
│   ├── edit_post.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   └── signup.html
└── uploads
    └── hp_Screenshot 2024-01-27 193234.png
```

*   `main.py`: The main FastAPI application file containing all the routes and logic.
*   `templates/`: Contains the Jinja2 templates for the HTML pages.
*   `static/`: Contains the static files (CSS, JavaScript, etc.).
*   `uploads/`: The directory where uploaded images are stored.
*   `README.md`: This file.