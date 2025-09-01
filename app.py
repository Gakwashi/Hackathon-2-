from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from supabase import create_client
from dotenv import load_dotenv
import os
import openai
import random

# Load environment variables
load_dotenv('file.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not OPENAI_API_KEY or not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing environment variables in file.env")

# Initialize OpenAI and Supabase
openai.api_key = OPENAI_API_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    response = supabase.table("users").select("*").eq("id", int(user_id)).execute()
    user = response.data[0] if response.data else None
    if user:
        return User(id=user['id'], email=user['email'])
    return None

# Routes
@app.route("/")
@login_required
def home():
    return render_template("index.html", email=current_user.email)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save user in Supabase
        supabase.table("users").insert({"email": email, "password": hashed}).execute()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        response = supabase.table("users").select("*").eq("email", email).execute()
        user = response.data[0] if response.data else None
        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(id=user['id'], email=user['email']))
            return redirect(url_for("home"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/api/recipes")
@login_required
def get_recipes():
    response = supabase.table("recipes").select("*").eq("user_id", int(current_user.id)).execute()
    recipes = response.data if response.data else []
    formatted = []
    for r in recipes:
        formatted.append({
            "title": r.get("title", "No Title"),
            "ingredients": r.get("ingredients", []),
            "instructions": r.get("instructions", ""),
            "tags": r.get("tags", []),
            "image": r.get("image", "https://placehold.co/600x400?text=No+Image")
        })
    return jsonify(formatted)

@app.route("/recommend", methods=["POST"])
@login_required
def recommend():
    data = request.json
    ingredients = data.get("ingredients", "").strip()
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    # Generate recipe using OpenAI
    prompt = f"Suggest a healthy recipe using: {ingredients}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    recipe_text = response.choices[0].text.strip()

    # Random placeholder image
    placeholder_id = random.randint(1, 1000)
    image_url = f"https://placehold.co/600x400?text=Recipe+{placeholder_id}"

    # Save recipe in Supabase
    supabase.table("recipes").insert({
        "user_id": int(current_user.id),
        "title": "AI Suggested Recipe",
        "ingredients": [i.strip() for i in ingredients.split(",")],
        "instructions": recipe_text,
        "tags": ["AI", "Custom"],
        "image": image_url
    }).execute()

    return jsonify({"recipe": recipe_text})

if __name__ == "__main__":
    app.run(debug=True)
