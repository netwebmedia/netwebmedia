/* ═══════════════════════════════════════════
   PokerPulse — Ad Tracking & Management
   ═══════════════════════════════════════════ */

const AdManager = {
    STORAGE_KEY: 'pokerpulse_ad_metrics',

    getMetrics() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        return data ? JSON.parse(data) : { impressions: {}, clicks: {}, ctr: {} };
    },

    saveMetrics(metrics) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(metrics));
    },

    trackImpression(advertiser, placement) {
        const metrics = this.getMetrics();
        const key = `${advertiser}_${placement}`;
        metrics.impressions[key] = (metrics.impressions[key] || 0) + 1;
        this.saveMetrics(metrics);
    },

    trackClick(advertiser, placement) {
        const metrics = this.getMetrics();
        const key = `${advertiser}_${placement}`;
        metrics.clicks[key] = (metrics.clicks[key] || 0) + 1;

        // Log to CRM activity
        if (typeof CRM !== 'undefined') {
            CRM.logActivity(`Ad click: ${advertiser} (${placement})`, 'ad_click');
        }

        this.saveMetrics(metrics);
    },

    getReport() {
        const metrics = this.getMetrics();
        const report = {};

        Object.keys(metrics.impressions).forEach(key => {
            const [advertiser, placement] = key.split('_');
            if (!report[advertiser]) report[advertiser] = { impressions: 0, clicks: 0 };
            report[advertiser].impressions += metrics.impressions[key] || 0;
            report[advertiser].clicks += metrics.clicks[key] || 0;
        });

        Object.keys(metrics.clicks).forEach(key => {
            const [advertiser] = key.split('_');
            if (!report[advertiser]) report[advertiser] = { impressions: 0, clicks: 0 };
            report[advertiser].clicks += metrics.clicks[key] || 0;
        });

        // Calculate CTR
        Object.keys(report).forEach(adv => {
            const r = report[adv];
            r.ctr = r.impressions > 0 ? ((r.clicks / r.impressions) * 100).toFixed(2) + '%' : '0%';
        });

        return report;
    }
};

/* ─── Global click handler ─── */
function trackAdClick(advertiser, placement) {
    AdManager.trackClick(advertiser, placement);
}

/* ─── Track impressions on page load ─── */
document.addEventListener('DOMContentLoaded', () => {
    // Track all visible ad cards
    document.querySelectorAll('.ad-card[data-advertiser]').forEach(card => {
        const advertiser = card.dataset.advertiser;
        const placement = card.dataset.placement;
        if (advertiser && placement) {
            AdManager.trackImpression(advertiser, placement);
        }
    });

    // Also track room cards as ad impressions
    document.querySelectorAll('.room-card[data-advertiser]').forEach(card => {
        AdManager.trackImpression(card.dataset.advertiser, 'rooms-grid');
    });
});
