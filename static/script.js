// DOM elements
const container = document.getElementById("recipeContainer");
const ingredientsInput = document.getElementById("ingredientsInput");
const searchBtn = document.getElementById("searchBtn");

// Initialize the app
function init() {
    loadRecipes();
    setupEventListeners();
}

// Load recipes from API
async function loadRecipes(ingredients = "") {
    try {
        container.innerHTML = `<div class="loading">Loading recipes</div>`;
        
        let url = "/api/recipes";
        if (ingredients) {
            url += `?ingredients=${encodeURIComponent(ingredients)}`;
            
            // Track search statistics
            trackStatistics("search", ingredients);
        }
        
        const response = await fetch(url);
        const recipes = await response.json();
        
        displayRecipes(recipes);
    } catch (error) {
        console.error("Error loading recipes:", error);
        container.innerHTML = `<div class="no-results">Error loading recipes. Please try again.</div>`;
    }
}

// Display recipes in the container
function displayRecipes(recipes) {
    container.innerHTML = "";
    
    if (recipes.length === 0) {
        container.innerHTML = `<div class="no-results">No recipes found. Try a different search.</div>`;
        return;
    }
    
    recipes.forEach(recipe => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <div class="card-img">
                <img src="${recipe.image}" alt="${recipe.title}">
            </div>
            <div class="card-content">
                <h3>${recipe.title}</h3>
                <div class="ingredients">
                    ${recipe.ingredients.map(ing => `<span>${ing}</span>`).join("")}
                </div>
                <p><strong>Instructions:</strong> ${recipe.instructions}</p>
                <div class="tags">
                    ${recipe.tags.map(tag => `<div class="tag">${tag}</div>`).join("")}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// Track usage statistics
async function trackStatistics(action, ingredients = "", recipeId = null) {
    try {
        await fetch("/api/statistics", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: action,
                ingredients: ingredients,
                recipe_id: recipeId
            })
        });
    } catch (error) {
        console.error("Error tracking statistics:", error);
    }
}

// Set up event listeners
function setupEventListeners() {
    searchBtn.addEventListener("click", () => {
        loadRecipes(ingredientsInput.value);
    });
    
    ingredientsInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            loadRecipes(ingredientsInput.value);
        }
    });
}

// Initialize the app when the DOM is loaded
document.addEventListener("DOMContentLoaded", init);
