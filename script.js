const container = document.getElementById("recipeContainer");
const ingredientsInput = document.getElementById("ingredientsInput");
const searchBtn = document.getElementById("searchBtn");

async function loadRecipes(ingredients="") {
    container.innerHTML = "<p>Loading recipes...</p>";

    if (ingredients) {
        await fetch("/recommend", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({ ingredients })
        });
    }

    const response = await fetch("/api/recipes");
    const recipes = await response.json();
    container.innerHTML = "";

    if (recipes.length === 0) {
        container.innerHTML = "<p>No recipes found.</p>";
        return;
    }

    recipes.forEach(r => {
        const card = document.createElement("div");
        card.className = "recipe-card";
        card.innerHTML = `
            <div class="card-img">
                <img src="${r.image}" alt="${r.title}">
            </div>
            <h3>${r.title}</h3>
            <p><strong>Ingredients:</strong> ${r.ingredients.join(", ")}</p>
            <p><strong>Instructions:</strong> ${r.instructions}</p>
            <div class="tags">${r.tags.map(tag => `<div class="tag">${tag}</div>`).join("")}</div>
        `;
        container.appendChild(card);
    });
}

searchBtn.addEventListener("click", () => loadRecipes(ingredientsInput.value));
ingredientsInput.addEventListener("keypress", e => { if (e.key==="Enter") loadRecipes(ingredientsInput.value); });

document.addEventListener("DOMContentLoaded", () => loadRecipes());
