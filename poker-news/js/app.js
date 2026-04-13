/* ═══════════════════════════════════════════
   PokerPulse — Main Application JS
   ═══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initFilterTabs();
    initNewsletterForms();
    initLoadMore();
});

/* ─── Mobile Menu Toggle ─── */
function initMobileMenu() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.getElementById('mainNav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', () => {
        nav.classList.toggle('open');
        toggle.textContent = nav.classList.contains('open') ? '✕' : '☰';
    });
}

/* ─── News Filter Tabs ─── */
function initFilterTabs() {
    const tabs = document.querySelectorAll('.filter-tab');
    const cards = document.querySelectorAll('.news-card');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const filter = tab.dataset.filter;

            cards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = 'flex';
                } else {
                    const category = card.dataset.category;
                    card.style.display = (category === filter || category === 'all') ? 'flex' : 'none';
                }
            });
        });
    });
}

/* ─── Newsletter Form Handlers ─── */
function initNewsletterForms() {
    const forms = document.querySelectorAll('#newsletterForm, #ctaNewsletterForm');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Get email from input
            const emailInput = form.querySelector('input[type="email"]');
            const nameInput = form.querySelector('input[name="firstName"]');

            const contact = {
                email: emailInput ? emailInput.value : '',
                firstName: nameInput ? nameInput.value : '',
                interest: data.interest || 'general',
                source: 'newsletter',
                subscribedAt: new Date().toISOString(),
                status: 'lead'
            };

            // Save to CRM
            CRM.addContact(contact);

            // Show success
            const btn = form.querySelector('button[type="submit"]');
            const originalText = btn.textContent;
            btn.textContent = 'Subscribed!';
            btn.style.background = '#00b894';

            if (emailInput) emailInput.value = '';
            if (nameInput) nameInput.value = '';

            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 3000);
        });
    });
}

/* ─── Load More ─── */
function initLoadMore() {
    const btn = document.getElementById('loadMore');
    if (!btn) return;

    btn.addEventListener('click', () => {
        btn.textContent = 'Loading...';
        setTimeout(() => {
            btn.textContent = 'No More Stories';
            btn.disabled = true;
            btn.style.opacity = '0.5';
        }, 1000);
    });
}
