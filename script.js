document.addEventListener('DOMContentLoaded', () => {
    const initSection = document.getElementById('init-section');
    const searchSection = document.getElementById('search-section');
    const videoInfo = document.getElementById('video-info');
    const initBtn = document.getElementById('init-btn');
    const initProgress = document.getElementById('init-progress');
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('main-search');
    const resultsGrid = document.getElementById('results-grid');
    const resultsStats = document.getElementById('results-stats');

    const API_BASE = 'http://localhost:8081';

    async function checkStatus() {
        try {
            const response = await fetch(`${API_BASE}/status`);
            const data = await response.json();
            
            videoInfo.textContent = `Library: ${data.video_name}`;

            if (data.is_indexed) {
                showSearch();
            } else {
                showInit();
            }
        } catch (error) {
            videoInfo.textContent = "Error: Backend not reachable";
            console.error(error);
        }
    }

    function showSearch() {
        initSection.classList.add('hidden');
        searchSection.classList.remove('hidden');
    }

    function showInit() {
        initSection.classList.remove('hidden');
        searchSection.classList.add('hidden');
    }

    initBtn.addEventListener('click', async () => {
        initBtn.classList.add('hidden');
        initProgress.classList.remove('hidden');

        try {
            const response = await fetch(`${API_BASE}/initialize`, { method: 'POST' });
            const data = await response.json();

            if (data.status === 'success') {
                showSearch();
            } else {
                alert(`Error: ${data.message}`);
                initBtn.classList.remove('hidden');
                initProgress.classList.add('hidden');
            }
        } catch (error) {
            alert("Failed to initialize. Check backend logs.");
            initBtn.classList.remove('hidden');
            initProgress.classList.add('hidden');
        }
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        resultsGrid.innerHTML = '<div class="spinner"></div>';
        resultsStats.classList.add('hidden');

        try {
            const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            renderResults(results);
        } catch (error) {
            resultsGrid.innerHTML = '<p>Error searching. Is the backend running?</p>';
        }
    }

    function renderResults(results) {
        resultsGrid.innerHTML = '';
        
        if (results.length === 0) {
            resultsGrid.innerHTML = '<p class="no-results">No matches found for this query.</p>';
            return;
        }

        resultsStats.classList.remove('hidden');
        document.getElementById('count').textContent = results.length;

        results.forEach(item => {
            const card = document.createElement('div');
            card.className = 'video-card';
            card.innerHTML = `
                <img src="${item.thumbnail}" alt="Video Frame" class="thumbnail-img" style="width: 100%; border-radius: 8px; margin-bottom: 10px; object-fit: cover; aspect-ratio: 16/9; background: #333;">
                <span class="match-type match-${item.matchType}">${item.matchType}</span>
                <h3 class="video-title"><span class="timestamp">${item.timestamp}</span></h3>
                <p class="match-context">${item.matchText}</p>
            `;
            resultsGrid.appendChild(card);
        });
    }

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // Initial check
    checkStatus();
});
