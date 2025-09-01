from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend requests

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/recipe")
def get_recipe():
    query = request.args.get("query", "nutritious meal")
    prompt = f"Give me a simple, healthy recipe using affordable ingredients for {query}. Keep it short and easy to follow."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    recipe_text = response.choices[0].message.content
    return jsonify({"recipe": recipe_text})

if __name__ == "__main__":
    app.run(debug=True)

