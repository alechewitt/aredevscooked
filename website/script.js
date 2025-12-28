// Load and display metrics from metrics_latest.json
(function() {
    'use strict';

    // Configuration
    const METRICS_URL = 'metrics_latest.json';

    // Utility functions
    function formatNumber(num) {
        return new Intl.NumberFormat('en-US').format(num);
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short'
        });
    }

    function formatPercentage(pct) {
        const sign = pct > 0 ? '+' : '';
        return `${sign}${pct.toFixed(2)}%`;
    }

    function getChangeClass(value) {
        if (value > 0) return 'positive';
        if (value < 0) return 'negative';
        return 'neutral';
    }

    function getBadgeHTML(badge) {
        return `<span class="badge badge-${badge}">${badge.replace(/_/g, ' ')}</span>`;
    }

    // Render functions
    function renderAggregateBadge(elementId, badge) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = getBadgeHTML(badge);
        }
    }

    function renderHeadcountCompany(companyName, data) {
        const current = formatNumber(data.current);
        const dataDate = data.data_date ? ` (as of ${data.data_date})` : '';

        let changesHTML = '';
        if (data.changes && Object.keys(data.changes).length > 0) {
            changesHTML = '<div class="company-changes">';
            for (const [period, change] of Object.entries(data.changes)) {
                const periodLabel = period.replace(/_/g, ' ').replace('ago', '');

                // Check if data is available
                if (change.value === null || change.pct === null) {
                    changesHTML += `
                        <div class="change-item">
                            <span class="change-label">${periodLabel}</span>
                            <span class="change-value" style="color: #6b7280;">N/A</span>
                            <span class="badge badge-neutral" style="font-size: 0.7rem; padding: 0.25rem 0.5rem; opacity: 0.5;">no data</span>
                        </div>
                    `;
                } else {
                    const valueClass = getChangeClass(change.value);
                    const valueText = change.value >= 0 ? `+${formatNumber(change.value)}` : formatNumber(change.value);
                    const pctText = formatPercentage(change.pct);

                    changesHTML += `
                        <div class="change-item">
                            <span class="change-label">${periodLabel}</span>
                            <span class="change-value ${valueClass}">${pctText}</span>
                            <span class="badge badge-${change.badge}" style="font-size: 0.7rem; padding: 0.25rem 0.5rem;">${change.badge}</span>
                        </div>
                    `;
                }
            }
            changesHTML += '</div>';
        }

        return `
            <div class="company-item">
                <div class="company-name">${companyName}</div>
                <div class="company-value">${current} employees${dataDate}</div>
                ${changesHTML}
            </div>
        `;
    }

    function renderJobPostingCompany(companyName, data) {
        const current = formatNumber(data.current);
        const collectionDate = data.collection_date ? ` (as of ${data.collection_date})` : '';

        let changesHTML = '';
        if (data.changes && Object.keys(data.changes).length > 0) {
            changesHTML = '<div class="company-changes">';
            for (const [period, change] of Object.entries(data.changes)) {
                const periodLabel = period.replace(/_/g, ' ').replace('ago', '');

                // Check if data is available
                if (change.value === null) {
                    changesHTML += `
                        <div class="change-item">
                            <span class="change-label">${periodLabel}</span>
                            <span class="change-value" style="color: #6b7280;">N/A</span>
                            <span class="badge badge-neutral" style="font-size: 0.7rem; padding: 0.25rem 0.5rem; opacity: 0.5;">no data</span>
                        </div>
                    `;
                } else {
                    const valueClass = getChangeClass(change.value);
                    const valueText = change.value >= 0 ? `+${change.value}` : change.value;

                    changesHTML += `
                        <div class="change-item">
                            <span class="change-label">${periodLabel}</span>
                            <span class="change-value ${valueClass}">${valueText} jobs</span>
                            <span class="badge badge-${change.badge}" style="font-size: 0.7rem; padding: 0.25rem 0.5rem;">${change.badge}</span>
                        </div>
                    `;
                }
            }
            changesHTML += '</div>';
        }

        return `
            <div class="company-item">
                <div class="company-name">${companyName}</div>
                <div class="company-value">${current} technical jobs${collectionDate}</div>
                ${changesHTML}
            </div>
        `;
    }

    function renderStockIndex(stockIndexData) {
        const indexValue = stockIndexData.current_value.toFixed(2);
        const changes = stockIndexData.changes;

        document.querySelector('.index-value .value').textContent = indexValue;

        const changesHTML = `
            <div class="index-change">
                <span class="period">30 Days</span>
                <span class="value ${getChangeClass(changes['30_day'])}">${formatPercentage(changes['30_day'])}</span>
            </div>
            <div class="index-change">
                <span class="period">1 Year</span>
                <span class="value ${getChangeClass(changes['1_year'])}">${formatPercentage(changes['1_year'])}</span>
            </div>
        `;

        document.getElementById('stockIndexChanges').innerHTML = changesHTML;
    }

    function renderMetrics(data) {
        // Update last updated timestamp
        document.getElementById('lastUpdated').textContent = `Last updated: ${formatDate(data.metadata.last_updated)}`;

        // Update AI summary
        document.getElementById('aiSummary').textContent = data.ai_summary;

        // Low-End: IT Consultancies
        renderAggregateBadge('lowEndHeadcountBadge', data.low_end.headcount.aggregate_badge);

        const lowEndHTML = Object.entries(data.low_end.headcount.companies)
            .map(([name, companyData]) => renderHeadcountCompany(name, companyData))
            .join('');
        document.getElementById('lowEndHeadcount').innerHTML = lowEndHTML;

        // Stock Index
        renderStockIndex(data.low_end.stock_index);

        // Medium-End: Big Tech
        renderAggregateBadge('mediumEndHeadcountBadge', data.medium_end.headcount.aggregate_badge);

        const mediumEndHTML = Object.entries(data.medium_end.headcount.companies)
            .map(([name, companyData]) => renderHeadcountCompany(name, companyData))
            .join('');
        document.getElementById('mediumEndHeadcount').innerHTML = mediumEndHTML;

        // High-End: AI Labs
        renderAggregateBadge('highEndJobsBadge', data.high_end.job_postings.aggregate_badge);

        const highEndHTML = Object.entries(data.high_end.job_postings.companies)
            .map(([name, companyData]) => renderJobPostingCompany(name, companyData))
            .join('');
        document.getElementById('highEndJobs').innerHTML = highEndHTML;
    }

    function showError(message) {
        const summaryCard = document.querySelector('.summary-card');
        summaryCard.innerHTML = `<div class="error">${message}</div>`;
    }

    // Load metrics on page load
    async function loadMetrics() {
        try {
            const response = await fetch(METRICS_URL);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            renderMetrics(data);
        } catch (error) {
            console.error('Failed to load metrics:', error);
            showError(`Failed to load market data: ${error.message}. Please try again later.`);
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadMetrics);
    } else {
        loadMetrics();
    }
})();
