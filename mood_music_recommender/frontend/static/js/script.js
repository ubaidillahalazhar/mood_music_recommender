document.addEventListener('DOMContentLoaded', () => {
    const moodForm = document.getElementById('mood-form');
    const moodSelect = document.getElementById('mood-select');
    const recommendationsList = document.getElementById('recommendations-list');
    const favoritesList = document.getElementById('favorites-list');
    const favoritesMoodFilter = document.getElementById('favorites-mood-filter');

    const moodInputSection = document.getElementById('mood-input-section');
    const favoritesSection = document.getElementById('favorites-section');
    const showRecommendationFormBtn = document.getElementById('show-recommendation-form');
    const showFavoritesBtn = document.getElementById('show-favorites');

    // --- Navigation ---
    showRecommendationFormBtn.addEventListener('click', () => {
        moodInputSection.classList.add('active-section');
        moodInputSection.classList.remove('hidden-section');
        favoritesSection.classList.add('hidden-section');
        favoritesSection.classList.remove('active-section');
        showRecommendationFormBtn.classList.add('active');
        showFavoritesBtn.classList.remove('active');
    });

    showFavoritesBtn.addEventListener('click', () => {
        favoritesSection.classList.add('active-section');
        favoritesSection.classList.remove('hidden-section');
        moodInputSection.classList.add('hidden-section');
        moodInputSection.classList.remove('active-section');
        showFavoritesBtn.classList.add('active');
        showRecommendationFormBtn.classList.remove('active');
        fetchFavorites(); // Load favorites when navigating to the section
    });

    // --- Mood Form Submission ---
    moodForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const selectedMood = moodSelect.value;

        if (!selectedMood) {
            alert('Please select a mood!');
            return;
        }

        recommendationsList.innerHTML = '<p style="text-align: center;">Loading recommendations...</p>';

        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mood: selectedMood,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch recommendations');
            }

            const data = await response.json();
            renderRecommendations(data.songs, selectedMood);

        } catch (error) {
            console.error('Error fetching recommendations:', error);
            recommendationsList.innerHTML = `<p style="color: red; text-align: center;">Error: ${error.message}. Please try again later.</p>`;
        }
    });

    // --- Render Recommendations ---
    function renderRecommendations(songs, mood) {
        recommendationsList.innerHTML = ''; // Clear previous recommendations
        if (songs.length === 0) {
            recommendationsList.innerHTML = `<p style="text-align: center;">No songs found for "${mood}" mood. Try another mood!</p>`;
            return;
        }

        songs.forEach(song => {
            const card = document.createElement('div');
            card.classList.add('music-card');
            card.innerHTML = `
                <h4>${song.title}</h4>
                <p>Artist: ${song.artist}</p>
                ${song.quote ? `<p class="quote">"${song.quote}"</p>` : ''}
                <div class="card-buttons">
                    <a href="${song.url}" target="_blank" class="action-button">Listen</a>
                    <button class="action-button add-favorite-btn"
                        data-title="${song.title}"
                        data-artist="${song.artist}"
                        data-url="${song.url}"
                        data-mood="${mood}">Add to Favorites</button>
                </div>
            `;
            recommendationsList.appendChild(card);
        });

        // Attach event listeners to new "Add to Favorites" buttons
        document.querySelectorAll('.add-favorite-btn').forEach(button => {
            button.addEventListener('click', addFavorite);
        });
    }

    // --- Add to Favorites ---
    async function addFavorite(event) {
        const button = event.target;
        const songData = {
            title: button.dataset.title,
            artist: button.dataset.artist,
            url: button.dataset.url, // Use generic 'url'
            mood: button.dataset.mood
        };

        try {
            const response = await fetch('/add_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(songData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to add to favorites');
            }

            const data = await response.json();
            alert(data.message);
            // Optionally update the favorites list immediately if on favorites page
            if (!favoritesSection.classList.contains('hidden-section')) {
                fetchFavorites();
            }

        } catch (error) {
            console.error('Error adding to favorites:', error);
            alert(`Error adding song to favorites: ${error.message}`);
        }
    }

    // --- Fetch and Render Favorites ---
    favoritesMoodFilter.addEventListener('change', fetchFavorites);

    async function fetchFavorites() {
        favoritesList.innerHTML = '<p style="text-align: center;">Loading favorites...</p>';
        try {
            const response = await fetch('/favorites');
            if (!response.ok) {
                throw new Error('Failed to fetch favorites');
            }
            const data = await response.json();
            const filterMood = favoritesMoodFilter.value;
            const filteredFavorites = filterMood === 'all'
                ? data.favorites
                : data.favorites.filter(fav => fav.mood.toLowerCase() === filterMood.toLowerCase());

            renderFavorites(filteredFavorites);

        } catch (error) {
            console.error('Error fetching favorites:', error);
            favoritesList.innerHTML = `<p style="color: red; text-align: center;">Error: ${error.message}.</p>`;
        }
    }

    function renderFavorites(favorites) {
        favoritesList.innerHTML = '';
        if (favorites.length === 0) {
            favoritesList.innerHTML = '<p style="text-align: center;">No favorite songs found for this category.</p>';
            return;
        }

        favorites.forEach(song => {
            const card = document.createElement('div');
            card.classList.add('music-card');
            card.innerHTML = `
                <h4>${song.title}</h4>
                <p>Artist: ${song.artist}</p>
                <p>Mood: ${song.mood}</p>
                <div class="card-buttons">
                    <a href="${song.url}" target="_blank" class="action-button">Listen</a>
                    <button class="action-button remove-button" data-url="${song.url}">Remove</button>
                </div>
            `;
            favoritesList.appendChild(card);
        });

        document.querySelectorAll('.remove-button').forEach(button => {
            button.addEventListener('click', deleteFavorite);
        });
    }

    // --- Delete Favorite ---
    async function deleteFavorite(event) {
        const button = event.target;
        const songUrl = button.dataset.url; // Use generic 'url' for deletion

        if (!confirm('Are you sure you want to remove this song from favorites?')) {
            return;
        }

        try {
            const response = await fetch('/delete_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: songUrl }) // Send generic 'url'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to remove from favorites');
            }

            const data = await response.json();
            alert(data.message);
            fetchFavorites(); // Refresh favorites list

        } catch (error) {
            console.error('Error deleting favorite:', error);
            alert(`Error removing song: ${error.message}`);
        }
    }

    // Initial load for active section (Recommendation form by default)
    showRecommendationFormBtn.click();
});
