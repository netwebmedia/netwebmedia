/* ═══════════════════════════════════════════
   PokerPulse — CRM System
   localStorage-based contact management
   ═══════════════════════════════════════════ */

const CRM = {
    STORAGE_KEY: 'pokerpulse_crm',
    ACTIVITY_KEY: 'pokerpulse_activity',

    /* ─── Data Access ─── */
    getContacts() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        return data ? JSON.parse(data) : this.getSeedData();
    },

    saveContacts(contacts) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(contacts));
    },

    getActivities() {
        const data = localStorage.getItem(this.ACTIVITY_KEY);
        return data ? JSON.parse(data) : [];
    },

    saveActivities(activities) {
        localStorage.setItem(this.ACTIVITY_KEY, JSON.stringify(activities));
    },

    /* ─── CRUD Operations ─── */
    addContact(contact) {
        const contacts = this.getContacts();
        contact.id = 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
        contact.createdAt = contact.createdAt || new Date().toISOString();
        contact.status = contact.status || 'lead';
        contact.tags = contact.tags || [];
        contact.notes = contact.notes || '';
        contacts.unshift(contact);
        this.saveContacts(contacts);
        this.logActivity(`New contact added: ${contact.email}`, 'contact_add');
        return contact;
    },

    updateContact(id, updates) {
        const contacts = this.getContacts();
        const idx = contacts.findIndex(c => c.id === id);
        if (idx === -1) return null;
        contacts[idx] = { ...contacts[idx], ...updates, updatedAt: new Date().toISOString() };
        this.saveContacts(contacts);
        this.logActivity(`Contact updated: ${contacts[idx].email}`, 'contact_update');
        return contacts[idx];
    },

    deleteContact(id) {
        const contacts = this.getContacts();
        const contact = contacts.find(c => c.id === id);
        const filtered = contacts.filter(c => c.id !== id);
        this.saveContacts(filtered);
        if (contact) this.logActivity(`Contact deleted: ${contact.email}`, 'contact_delete');
    },

    searchContacts(query) {
        const contacts = this.getContacts();
        const q = query.toLowerCase();
        return contacts.filter(c =>
            (c.email && c.email.toLowerCase().includes(q)) ||
            (c.firstName && c.firstName.toLowerCase().includes(q)) ||
            (c.lastName && c.lastName.toLowerCase().includes(q)) ||
            (c.tags && c.tags.some(t => t.toLowerCase().includes(q)))
        );
    },

    /* ─── Activity Log ─── */
    logActivity(message, type) {
        const activities = this.getActivities();
        activities.unshift({
            id: 'a_' + Date.now(),
            message,
            type,
            timestamp: new Date().toISOString()
        });
        // Keep last 100
        if (activities.length > 100) activities.length = 100;
        this.saveActivities(activities);
    },

    /* ─── Analytics ─── */
    getStats() {
        const contacts = this.getContacts();
        const now = new Date();
        const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);

        return {
            total: contacts.length,
            active: contacts.filter(c => c.status === 'active').length,
            leads: contacts.filter(c => c.status === 'lead').length,
            inactive: contacts.filter(c => c.status === 'inactive').length,
            thisWeek: contacts.filter(c => new Date(c.createdAt) > weekAgo).length,
            bySource: contacts.reduce((acc, c) => {
                const src = c.source || 'unknown';
                acc[src] = (acc[src] || 0) + 1;
                return acc;
            }, {}),
            byInterest: contacts.reduce((acc, c) => {
                const int = c.interest || 'general';
                acc[int] = (acc[int] || 0) + 1;
                return acc;
            }, {})
        };
    },

    /* ─── Export ─── */
    exportCSV() {
        const contacts = this.getContacts();
        const headers = ['ID', 'First Name', 'Last Name', 'Email', 'Status', 'Interest', 'Source', 'Tags', 'Notes', 'Created'];
        const rows = contacts.map(c => [
            c.id,
            c.firstName || '',
            c.lastName || '',
            c.email || '',
            c.status || '',
            c.interest || '',
            c.source || '',
            (c.tags || []).join(';'),
            (c.notes || '').replace(/,/g, ';'),
            c.createdAt || ''
        ]);

        const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pokerpulse_contacts_${new Date().toISOString().slice(0,10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        this.logActivity('Contacts exported to CSV', 'export');
    },

    /* ─── Seed Data ─── */
    getSeedData() {
        const seed = [
            { id: 'c_seed_001', firstName: 'Jake', lastName: 'Rivera', email: 'jake.r@pokerpro.com', status: 'active', interest: 'tournaments', source: 'newsletter', tags: ['wsop', 'high-roller'], notes: 'Regular tournament player, WSOP Main Event qualifier', createdAt: '2026-03-15T10:00:00Z' },
            { id: 'c_seed_002', firstName: 'Sarah', lastName: 'Chen', email: 'sarah.chen@gmail.com', status: 'active', interest: 'strategy', source: 'newsletter', tags: ['gto', 'cash-games'], notes: 'Interested in GTO strategy content', createdAt: '2026-03-18T14:30:00Z' },
            { id: 'c_seed_003', firstName: 'Marcus', lastName: 'Williams', email: 'mwilliams@cardshark.io', status: 'lead', interest: 'online', source: 'ad-click', tags: ['ggpoker', 'online'], notes: 'Clicked GGPoker ad, new to online poker', createdAt: '2026-04-01T09:15:00Z' },
            { id: 'c_seed_004', firstName: 'Emma', lastName: 'Johansson', email: 'emma.j@pokerblog.se', status: 'active', interest: 'all', source: 'newsletter', tags: ['ept', 'live-poker', 'blogger'], notes: 'Swedish poker blogger, covers EPT events', createdAt: '2026-02-20T16:45:00Z' },
            { id: 'c_seed_005', firstName: 'David', lastName: 'Kim', email: 'dkim@pokervlog.com', status: 'active', interest: 'live', source: 'referral', tags: ['vlogger', 'las-vegas'], notes: 'Poker vlogger, planning WSOP 2026 coverage', createdAt: '2026-03-22T11:20:00Z' },
            { id: 'c_seed_006', firstName: 'Alex', lastName: 'Thompson', email: 'alex.t@888poker.fans', status: 'lead', interest: 'online', source: 'ad-click', tags: ['888poker', 'freeroll'], notes: 'Signed up through 888poker no-deposit ad', createdAt: '2026-04-05T08:00:00Z' },
            { id: 'c_seed_007', firstName: 'Maria', lastName: 'Santos', email: 'maria.s@pokergals.com', status: 'active', interest: 'tournaments', source: 'newsletter', tags: ['wsop', 'women-in-poker'], notes: 'Women in Poker advocate, tournament circuit regular', createdAt: '2026-01-10T13:30:00Z' },
            { id: 'c_seed_008', firstName: 'Ryan', lastName: 'O\'Brien', email: 'ryan.ob@cardplayer.ie', status: 'active', interest: 'live', source: 'newsletter', tags: ['irish-open', 'ept'], notes: 'Irish poker fan, covers European circuit', createdAt: '2026-03-01T10:45:00Z' },
            { id: 'c_seed_009', firstName: 'Tommy', lastName: 'Nguyen', email: 'tommy.n@acr.fan', status: 'lead', interest: 'online', source: 'ad-click', tags: ['acr', 'crypto'], notes: 'ACR player, interested in crypto deposits', createdAt: '2026-04-08T15:00:00Z' },
            { id: 'c_seed_010', firstName: 'Lisa', lastName: 'Bergstrom', email: 'lisa.b@pokerstrategy.net', status: 'inactive', interest: 'strategy', source: 'newsletter', tags: ['plo', 'mixed-games'], notes: 'PLO specialist, unsubscribed from daily but keeps weekly', createdAt: '2025-12-05T09:00:00Z' },
            { id: 'c_seed_011', firstName: 'Chris', lastName: 'Patel', email: 'chris.p@pokergrind.com', status: 'active', interest: 'tournaments', source: 'newsletter', tags: ['wpt', 'mid-stakes'], notes: 'WPT circuit regular, $1K-$5K buy-in range', createdAt: '2026-02-14T12:00:00Z' },
            { id: 'c_seed_012', firstName: 'Jenny', lastName: 'Martinez', email: 'jenny.m@pokernewbie.com', status: 'lead', interest: 'strategy', source: 'organic', tags: ['beginner', 'hand-rankings'], notes: 'New to poker, found us via Google search for hand rankings', createdAt: '2026-04-10T17:30:00Z' },
        ];
        this.saveContacts(seed);
        return seed;
    }
};

/* ─── CRM Dashboard Renderer ─── */
const CRMDashboard = {
    init() {
        if (!document.querySelector('.crm-page')) return;
        this.renderStats();
        this.renderTable();
        this.renderActivities();
        this.initSearch();
        this.initAddForm();
        this.initExport();
    },

    renderStats() {
        const stats = CRM.getStats();
        const container = document.getElementById('crmStats');
        if (!container) return;

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${stats.total}</div>
                <div class="stat-label">Total Contacts</div>
                <div class="stat-change change-up">+${stats.thisWeek} this week</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.active}</div>
                <div class="stat-label">Active Subscribers</div>
                <div class="stat-change change-up">${Math.round(stats.active / stats.total * 100)}% of total</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.leads}</div>
                <div class="stat-label">New Leads</div>
                <div class="stat-change change-up">Ready for outreach</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${Object.keys(stats.bySource).length}</div>
                <div class="stat-label">Traffic Sources</div>
                <div class="stat-change">${Object.entries(stats.bySource).map(([k,v]) => `${k}: ${v}`).join(', ')}</div>
            </div>
        `;
    },

    renderTable(contacts) {
        const tbody = document.getElementById('crmTableBody');
        if (!tbody) return;

        const data = contacts || CRM.getContacts();

        tbody.innerHTML = data.map(c => `
            <tr data-id="${c.id}">
                <td><strong>${c.firstName || ''} ${c.lastName || ''}</strong></td>
                <td>${c.email || ''}</td>
                <td><span class="status-badge status-${c.status}">${c.status}</span></td>
                <td>${c.interest || 'general'}</td>
                <td>${c.source || 'unknown'}</td>
                <td>${c.tags ? c.tags.slice(0, 2).join(', ') : ''}</td>
                <td>
                    <button class="btn btn-sm btn-outline crm-edit-btn" data-id="${c.id}">Edit</button>
                    <button class="btn btn-sm btn-outline crm-delete-btn" data-id="${c.id}" style="color:var(--accent-red);border-color:var(--accent-red)">×</button>
                </td>
            </tr>
        `).join('');

        // Wire up delete buttons
        tbody.querySelectorAll('.crm-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (confirm('Delete this contact?')) {
                    CRM.deleteContact(btn.dataset.id);
                    this.renderStats();
                    this.renderTable();
                    this.renderActivities();
                }
            });
        });

        // Wire up edit buttons
        tbody.querySelectorAll('.crm-edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const contacts = CRM.getContacts();
                const contact = contacts.find(c => c.id === btn.dataset.id);
                if (!contact) return;

                const newStatus = prompt('Update status (active/lead/inactive):', contact.status);
                if (newStatus && ['active', 'lead', 'inactive'].includes(newStatus)) {
                    CRM.updateContact(btn.dataset.id, { status: newStatus });
                    this.renderStats();
                    this.renderTable();
                    this.renderActivities();
                }
            });
        });
    },

    renderActivities() {
        const container = document.getElementById('activityFeed');
        if (!container) return;

        const activities = CRM.getActivities().slice(0, 10);

        if (activities.length === 0) {
            container.innerHTML = '<div class="activity-item">No activity yet</div>';
            return;
        }

        container.innerHTML = activities.map(a => {
            const date = new Date(a.timestamp);
            const timeAgo = getTimeAgo(date);
            return `
                <div class="activity-item">
                    ${a.message}
                    <span class="activity-time">${timeAgo}</span>
                </div>
            `;
        }).join('');
    },

    initSearch() {
        const input = document.getElementById('crmSearch');
        if (!input) return;

        input.addEventListener('input', () => {
            const query = input.value.trim();
            if (query.length < 2) {
                this.renderTable();
            } else {
                this.renderTable(CRM.searchContacts(query));
            }
        });
    },

    initAddForm() {
        const form = document.getElementById('addContactForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(form);

            const contact = {
                firstName: formData.get('firstName'),
                lastName: formData.get('lastName'),
                email: formData.get('email'),
                status: formData.get('status') || 'lead',
                interest: formData.get('interest') || 'general',
                source: 'manual',
                tags: formData.get('tags') ? formData.get('tags').split(',').map(t => t.trim()) : []
            };

            CRM.addContact(contact);
            form.reset();
            this.renderStats();
            this.renderTable();
            this.renderActivities();
        });
    },

    initExport() {
        const btn = document.getElementById('exportCsv');
        if (!btn) return;
        btn.addEventListener('click', () => CRM.exportCSV());
    }
};

/* ─── Helpers ─── */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

/* ─── Init on load ─── */
document.addEventListener('DOMContentLoaded', () => {
    CRMDashboard.init();
});
