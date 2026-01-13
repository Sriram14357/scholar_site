async function loadScholar() {
    try {
        const response = await fetch('assets/publications.json');
        const papers = await response.json();
        const list = document.getElementById('paper-list');
        list.innerHTML = '';

        papers.forEach(p => {
            const card = document.createElement('div');
            card.className = 'paper-card';
            card.innerHTML = `
                <div class="paper-info">
                    <h3 class="paper-title">${p.title}</h3>
                    <p class="paper-authors">${p.authors}</p>
                    <p class="paper-meta">${p.journal} (${p.year}) — Citations: ${p.citations}</p>
                </div>
                <div class="badges">
                    ${p.doi ? `
                        <div class='altmetric-embed' data-badge-type='donut' data-doi="${p.doi}"></div>
                        <a href="https://plu.mx/plum/a/?doi=${p.doi}" class="plumx-details" data-site="plum" data-hide-when-empty="true"></a>
                    ` : '<span style="color:#ccc; font-size:10px;">No DOI</span>'}
                </div>
            `;
            list.appendChild(card);
        });

        if (window._altmetric_embed_init) _altmetric_embed_init();
        if (window.__plumX) window.__plumX.render();
    } catch (e) {
        document.getElementById('paper-list').innerHTML = "No data found. Please run the Python script first.";
    }
}
window.onload = loadScholar;