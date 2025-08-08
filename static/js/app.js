// CityScout Web UI JavaScript

class CityScout {
    constructor() {
        this.form = document.getElementById('analysisForm');
        this.loading = document.getElementById('loading');
        this.error = document.getElementById('error');
        this.results = document.getElementById('results');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        
        this.bindEvents();
    }
    
    bindEvents() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeCity();
        });
        
        document.getElementById('toggleJson').addEventListener('click', () => {
            this.toggleJsonDisplay();
        });
    }
    
    async analyzeCity() {
        const city = document.getElementById('city').value.trim();
        const state = document.getElementById('state').value.trim();
        
        if (!city || !state) {
            this.showError('Please enter both city and state.');
            return;
        }
        
        this.showLoading();
        this.hideError();
        this.hideResults();
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ city, state })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.data);
            } else {
                this.showError(data.error || 'An error occurred while analyzing the city.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoading();
        }
    }
    
    displayResults(data) {
        // Update city name and date
        document.getElementById('cityName').textContent = `${data.city}, ${data.state}`;
        document.getElementById('analysisDate').textContent = 
            `Analysis generated on ${new Date().toLocaleDateString()}`;
        
        // Update demographics
        document.getElementById('population').textContent = 
            this.formatNumber(data.total_population || data.population);
        document.getElementById('growth').textContent = 
            this.formatPercentage(data.population_growth_5yr);
        document.getElementById('income').textContent = 
            this.formatCurrency(data.median_household_income);
        document.getElementById('unemployment').textContent = 
            this.formatPercentage(data.unemployment_rate);
        
        // Generate insights
        this.generateInsights(data);
        
        // Display JSON data
        document.getElementById('jsonData').textContent = 
            JSON.stringify(data, null, 2);
        
        this.showResults();
    }
    
    generateInsights(data) {
        const insights = [];
        const insightsContainer = document.getElementById('insights');
        
        // Population insights
        if (data.total_population || data.population) {
            const population = data.total_population || data.population;
            if (population > 1000000) {
                insights.push(`${data.city} is a major metropolitan area with ${this.formatNumber(population)} residents.`);
            } else if (population > 500000) {
                insights.push(`${data.city} is a substantial city with ${this.formatNumber(population)} residents.`);
            } else if (population > 100000) {
                insights.push(`${data.city} is a mid-size city with ${this.formatNumber(population)} residents.`);
            } else {
                insights.push(`${data.city} is a smaller city with ${this.formatNumber(population)} residents.`);
            }
        }
        
        // Growth insights
        if (data.population_growth_5yr !== undefined) {
            const growth = data.population_growth_5yr;
            if (growth > 10) {
                insights.push(`Rapid population growth of ${this.formatPercentage(growth)} over the past 5 years.`);
            } else if (growth > 5) {
                insights.push(`Strong population growth of ${this.formatPercentage(growth)} over the past 5 years.`);
            } else if (growth > 0) {
                insights.push(`Moderate population growth of ${this.formatPercentage(growth)} over the past 5 years.`);
            } else if (growth < 0) {
                insights.push(`Population decline of ${this.formatPercentage(Math.abs(growth))} over the past 5 years.`);
            } else {
                insights.push(`Population has remained stable over the past 5 years.`);
            }
        }
        
        // Income insights (demographic context only)
        if (data.median_household_income) {
            const income = data.median_household_income;
            const nationalMedian = 70000;
            
            if (income > nationalMedian * 1.3) {
                insights.push(`Median household income of ${this.formatCurrency(income)} is significantly above national average.`);
            } else if (income > nationalMedian * 1.1) {
                insights.push(`Median household income of ${this.formatCurrency(income)} is above national average.`);
            } else if (income < nationalMedian * 0.8) {
                insights.push(`Median household income of ${this.formatCurrency(income)} is below national average.`);
            } else {
                insights.push(`Median household income of ${this.formatCurrency(income)} is close to national average.`);
            }
        }
        
        // Employment insights (demographic context only)
        if (data.unemployment_rate !== undefined) {
            const unemployment = data.unemployment_rate;
            if (unemployment < 3) {
                insights.push(`Very low unemployment rate of ${this.formatPercentage(unemployment)}.`);
            } else if (unemployment < 5) {
                insights.push(`Low unemployment rate of ${this.formatPercentage(unemployment)}.`);
            } else if (unemployment > 8) {
                insights.push(`Higher unemployment rate of ${this.formatPercentage(unemployment)}.`);
            } else {
                insights.push(`Unemployment rate of ${this.formatPercentage(unemployment)} is around national average.`);
            }
        }
        
        // Display insights
        insightsContainer.innerHTML = '';
        insights.forEach(insight => {
            const div = document.createElement('div');
            div.className = 'insight-item';
            div.textContent = insight;
            insightsContainer.appendChild(div);
        });
        
        if (insights.length === 0) {
            insightsContainer.innerHTML = '<div class="insight-item">No specific insights available with current data.</div>';
        }
    }
    
    formatNumber(num) {
        if (!num) return 'N/A';
        if (num >= 1000000) {
            return Math.round(num / 100000) / 10 + 'M';
        } else if (num >= 1000) {
            return Math.round(num / 100) / 10 + 'K';
        }
        return num.toLocaleString();
    }
    
    formatCurrency(amount) {
        if (!amount) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            maximumFractionDigits: 0
        }).format(amount);
    }
    
    formatPercentage(value) {
        if (value === undefined || value === null) return 'N/A';
        return value.toFixed(1) + '%';
    }
    
    showLoading() {
        this.loading.style.display = 'block';
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.querySelector('.btn-text').style.display = 'none';
        this.analyzeBtn.querySelector('.loading-spinner').style.display = 'inline';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.querySelector('.btn-text').style.display = 'inline';
        this.analyzeBtn.querySelector('.loading-spinner').style.display = 'none';
    }
    
    showError(message) {
        this.error.textContent = message;
        this.error.style.display = 'block';
    }
    
    hideError() {
        this.error.style.display = 'none';
    }
    
    showResults() {
        this.results.style.display = 'block';
        this.results.classList.add('show');
        this.results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    hideResults() {
        this.results.style.display = 'none';
        this.results.classList.remove('show');
    }
    
    toggleJsonDisplay() {
        const jsonData = document.getElementById('jsonData');
        const toggleBtn = document.getElementById('toggleJson');
        
        if (jsonData.style.display === 'none') {
            jsonData.style.display = 'block';
            toggleBtn.textContent = 'Hide JSON Data';
        } else {
            jsonData.style.display = 'none';
            toggleBtn.textContent = 'Show JSON Data';
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CityScout();
});
