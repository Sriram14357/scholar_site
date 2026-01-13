async function loadScholar() {
    try {
        console.log('Fetching publications.json...');
        const response = await fetch('assets/publications.json');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const papers = await response.json();
        console.log('Loaded papers:', papers.length);
        
        // Sort papers by year (latest to oldest)
        papers.sort((a, b) => b.year - a.year);
        
        const list = document.getElementById('paper-list');
        list.innerHTML = '';

        if (papers.length === 0) {
            list.innerHTML = '<p>No publications found.</p>';
            return;
        }

        papers.forEach(p => {
            const card = document.createElement('div');
            card.className = 'paper-card';
            const titleLink = p.doi 
                ? `<a href="https://doi.org/${p.doi}" target="_blank" rel="noopener noreferrer">${p.title}</a>`
                : p.title;
            card.innerHTML = `
                <div class="paper-info">
                    <h3 class="paper-title">${titleLink}</h3>
                    <p class="paper-authors">${p.authors}</p>
                    <p class="paper-meta">${p.journal} (${p.year}) — Citations: ${p.citations}</p>
                    ${p.impact_factor ? `<p class="paper-impact">${p.impact_factor} | <a href="https://sci-hub.st/${p.doi}" target="_blank" rel="noopener noreferrer" style="color:#d32f2f; text-decoration:none;"> 🐦‍⬛ Sci-Hub</a></p>` : ''}
                </div>
                <div class="badges">
                    ${p.doi ? `
                        <div class='altmetric-embed' data-badge-type='donut' data-doi="${p.doi}"></div>
                        <a href="https://plu.mx/plum/a/?doi=${p.doi}" 
                           class="plumx-plum-print-popup plum-liberty-theme"
                           data-popup="right"
                           data-size="medium"
                           data-hide-when-empty="true"></a>
                    ` : '<span style="color:#ccc; font-size:10px;">No DOI</span>'}
                </div>
            `;
            list.appendChild(card);
        });

        // Initialize Altmetric badges
        if (window._altmetric_embed_init) {
            _altmetric_embed_init();
        }
        
        // Initialize PlumX widgets after dynamically adding them with delay
        setTimeout(() => {
            if (window.__plumX && window.__plumX.widgets) {
                window.__plumX.widgets.init();
            }
        }, 1000);
    } catch (e) {
        console.error('Error loading publications:', e);
        document.getElementById('paper-list').innerHTML = `Error loading data: ${e.message}. Check console for details.`;
    }
}
window.onload = loadScholar;