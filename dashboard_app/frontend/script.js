// Natural Language to SQL Dashboard - JavaScript
class Dashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.currentResults = null;
        this.currentChart = null;
        this.queryHistory = [];
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkAPIConnection();
        await this.loadSuggestedQuestions();
        await this.loadKPIs();
        await this.loadDashboardCharts();
    }

    setupEventListeners() {
        // Query form submission
        document.getElementById('query-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitQuery();
        });

        // Chart creation
        document.getElementById('create-chart-btn').addEventListener('click', () => {
            this.showChart();
        });

        // Chart update
        document.getElementById('update-chart-btn').addEventListener('click', () => {
            this.updateChart();
        });

        // Export CSV
        document.getElementById('export-csv-btn').addEventListener('click', () => {
            this.exportToCSV();
        });

        // Error details toggle
        document.getElementById('show-error-details').addEventListener('click', () => {
            const details = document.getElementById('error-details');
            details.style.display = details.style.display === 'none' ? 'block' : 'none';
        });

        // Input focus handling
        document.getElementById('question-input').addEventListener('focus', () => {
            document.getElementById('dashboard-section').style.display = 'none';
        });

        // Enter key handling
        document.getElementById('question-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.submitQuery();
            }
        });
    }

    async checkAPIConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                this.updateStatus('connected', 'Connected');
            } else {
                this.updateStatus('disconnected', 'API Error');
            }
        } catch (error) {
            this.updateStatus('disconnected', 'Disconnected');
            console.error('API connection failed:', error);
        }
    }

    updateStatus(status, text) {
        const indicator = document.querySelector('#status-indicator i');
        const statusText = document.getElementById('status-text');
        
        indicator.className = `fas fa-circle me-1 ${
            status === 'connected' ? 'text-success' : 
            status === 'loading' ? 'text-warning' : 'text-danger'
        }`;
        statusText.textContent = text;
    }

    async loadSuggestedQuestions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/suggestions`);
            if (response.ok) {
                const data = await response.json();
                this.displaySuggestedQuestions(data.suggestions);
            }
        } catch (error) {
            console.error('Failed to load suggestions:', error);
        }
    }

    displaySuggestedQuestions(suggestions) {
        const container = document.getElementById('suggested-questions');
        container.innerHTML = '';

        // Flatten categorized suggestions
        const allSuggestions = [];
        if (typeof suggestions === 'object' && !Array.isArray(suggestions)) {
            Object.values(suggestions).forEach(categoryQuestions => {
                allSuggestions.push(...categoryQuestions);
            });
        } else {
            allSuggestions.push(...suggestions);
        }

        allSuggestions.slice(0, 8).forEach(question => {
            const item = document.createElement('div');
            item.className = 'list-group-item list-group-item-action suggested-question';
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div class="text-truncate-multiline">
                        <i class="fas fa-lightbulb text-warning me-2"></i>
                        ${question}
                    </div>
                </div>
            `;
            
            item.addEventListener('click', () => {
                document.getElementById('question-input').value = question;
                this.submitQuery();
            });
            
            container.appendChild(item);
        });
    }

    async loadKPIs() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/kpis`);
            if (response.ok) {
                const data = await response.json();
                this.displayKPIs(data.kpis);
            }
        } catch (error) {
            console.error('Failed to load KPIs:', error);
        }
    }

    displayKPIs(kpis) {
        const container = document.getElementById('kpi-cards');
        container.innerHTML = '';

        // Define key metrics to display
        const keyMetrics = [
            { key: 'total_revenue', label: 'Total Revenue', icon: 'fas fa-dollar-sign', format: 'currency' },
            { key: 'total_orders', label: 'Total Orders', icon: 'fas fa-shopping-cart', format: 'number' },
            { key: 'total_customers', label: 'Customers', icon: 'fas fa-users', format: 'number' },
            { key: 'average_order_value', label: 'Avg Order Value', icon: 'fas fa-chart-line', format: 'currency' }
        ];

        keyMetrics.forEach(metric => {
            let value = this.getNestedValue(kpis, metric.key);
            if (value !== undefined && value !== null) {
                const formattedValue = this.formatValue(value, metric.format);
                
                const card = document.createElement('div');
                card.className = 'card kpi-card text-white mb-2';
                card.innerHTML = `
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <div class="kpi-value">${formattedValue}</div>
                                <div class="kpi-label">${metric.label}</div>
                            </div>
                            <div>
                                <i class="${metric.icon} fa-2x opacity-75"></i>
                            </div>
                        </div>
                    </div>
                `;
                
                container.appendChild(card);
            }
        });
    }

    getNestedValue(obj, key) {
        // Handle nested object structure
        if (typeof obj === 'object') {
            // Check direct key
            if (obj[key] !== undefined) {
                return obj[key];
            }
            
            // Check in nested categories
            for (const category of Object.values(obj)) {
                if (typeof category === 'object' && category[key] !== undefined) {
                    return category[key];
                }
            }
        }
        return undefined;
    }

    formatValue(value, format) {
        if (value === null || value === undefined) return 'N/A';
        
        switch (format) {
            case 'currency':
                return new Intl.NumberFormat('en-US', { 
                    style: 'currency', 
                    currency: 'USD',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                }).format(value);
            case 'number':
                return new Intl.NumberFormat('en-US').format(value);
            case 'percentage':
                return `${value.toFixed(1)}%`;
            default:
                return value.toString();
        }
    }

    async submitQuery() {
        const questionInput = document.getElementById('question-input');
        const question = questionInput.value.trim();
        
        if (!question) {
            this.showError('Please enter a question');
            return;
        }

        // Show loading
        this.showLoading(true);
        this.updateStatus('loading', 'Processing...');
        
        console.log('Submitting query:', question);

        try {
            const response = await fetch(`${this.apiBaseUrl}/query/natural`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                this.displayResults(data);
                this.addToHistory(question, data.query.sql_query);
                this.updateStatus('connected', 'Connected');
            } else {
                this.showError(data.error, data);
                this.updateStatus('connected', 'Connected');
            }
        } catch (error) {
            console.error('Error submitting query:', error);
            this.showError('Network error: Unable to connect to the server');
            this.updateStatus('disconnected', 'Connection Error');
        } finally {
            console.log('Hiding loading modal');
            this.showLoading(false);
        }
    }

    displayResults(data) {
        this.currentResults = data;
        
        // Hide dashboard, show results
        document.getElementById('dashboard-section').style.display = 'none';
        document.getElementById('results-section').style.display = 'block';
        document.getElementById('results-section').classList.add('slide-in-up');

        // Show query info
        const queryInfo = document.getElementById('query-info');
        queryInfo.style.display = 'block';
        queryInfo.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <strong>Question:</strong> ${data.query.question}<br>
                    <strong>Generated SQL:</strong> 
                    <code class="bg-light p-1 rounded">${data.query.sql_query}</code>
                </div>
                <div class="col-md-4 text-end">
                    <small class="text-muted">
                        Results: ${data.result.row_count} rows<br>
                        Model: ${data.query.model_used}
                    </small>
                </div>
            </div>
        `;

        // Display table
        this.displayTable(data.result.data, data.result.columns);
    }

    displayTable(data, columns) {
        const container = document.getElementById('results-table-container');
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No results found.</div>';
            return;
        }

        // Create table
        const table = document.createElement('table');
        table.className = 'table table-striped table-hover results-table';

        // Create header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column;
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Create body
        const tbody = document.createElement('tbody');
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            
            columns.forEach(column => {
                const td = document.createElement('td');
                const value = row[column];
                
                // Format value based on type
                if (typeof value === 'number') {
                    if (column.toLowerCase().includes('price') || 
                        column.toLowerCase().includes('revenue') || 
                        column.toLowerCase().includes('total')) {
                        td.textContent = this.formatValue(value, 'currency');
                    } else if (value % 1 === 0) {
                        td.textContent = this.formatValue(value, 'number');
                    } else {
                        td.textContent = value.toFixed(2);
                    }
                } else {
                    td.textContent = value || 'N/A';
                }
                
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        container.innerHTML = '';
        container.appendChild(table);
    }

    showChart() {
        if (!this.currentResults) return;
        
        document.getElementById('chart-section').style.display = 'block';
        document.getElementById('chart-section').scrollIntoView({ behavior: 'smooth' });
        this.updateChart();
    }

    updateChart() {
        if (!this.currentResults) return;

        const chartType = document.getElementById('chart-type-select').value;
        const data = this.currentResults.result.data;
        const columns = this.currentResults.result.columns;

        // Analyze data and show axis information
        const axisInfo = this.analyzeDataForVisualization(data, columns, chartType);
        this.displayAxisInformation(axisInfo, chartType);

        this.createChart('results-chart', data, columns, chartType, axisInfo);
    }

    createChart(canvasId, data, columns, type = 'bar', axisInfo = null) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        // Destroy existing chart
        if (this.currentChart) {
            this.currentChart.destroy();
        }

        // Prepare data for chart
        const chartData = this.prepareChartData(data, columns, type);
        
        this.currentChart = new Chart(ctx, {
            type: type,
            data: chartData,
            options: this.getChartOptions(type, axisInfo)
        });
    }

    analyzeDataForVisualization(data, columns, chartType) {
        if (!data || data.length === 0) return null;

        const analysis = {
            xAxis: null,
            yAxis: [],
            recommendations: [],
            dataTypes: {}
        };

        // Analyze each column
        columns.forEach(col => {
            const values = data.map(row => row[col]);
            const nonNullValues = values.filter(v => v !== null && v !== undefined);
            
            if (nonNullValues.length === 0) return;

            // Determine data type
            const firstValue = nonNullValues[0];
            if (typeof firstValue === 'number') {
                analysis.dataTypes[col] = 'numeric';
            } else if (this.isDateString(firstValue)) {
                analysis.dataTypes[col] = 'date';
            } else {
                analysis.dataTypes[col] = 'categorical';
            }
        });

        // Determine best X and Y axes based on chart type and data
        if (chartType === 'pie' || chartType === 'doughnut') {
            // For pie charts, use first categorical column as labels and first numeric as values
            const categoricalCols = columns.filter(col => analysis.dataTypes[col] === 'categorical');
            const numericCols = columns.filter(col => analysis.dataTypes[col] === 'numeric');
            
            analysis.xAxis = categoricalCols[0] || columns[0];
            analysis.yAxis = numericCols.slice(0, 1);
            
            analysis.recommendations.push(`Categories: ${analysis.xAxis}`);
            analysis.recommendations.push(`Values: ${analysis.yAxis.join(', ')}`);
        } else {
            // For bar/line charts
            const categoricalCols = columns.filter(col => analysis.dataTypes[col] === 'categorical');
            const dateCols = columns.filter(col => analysis.dataTypes[col] === 'date');
            const numericCols = columns.filter(col => analysis.dataTypes[col] === 'numeric');

            // X-axis preference: dates > categorical > first column
            if (dateCols.length > 0) {
                analysis.xAxis = dateCols[0];
                analysis.recommendations.push(`X-axis (Time): ${analysis.xAxis}`);
            } else if (categoricalCols.length > 0) {
                analysis.xAxis = categoricalCols[0];
                analysis.recommendations.push(`X-axis (Categories): ${analysis.xAxis}`);
            } else {
                analysis.xAxis = columns[0];
                analysis.recommendations.push(`X-axis: ${analysis.xAxis}`);
            }

            // Y-axis: all numeric columns
            analysis.yAxis = numericCols.length > 0 ? numericCols : columns.filter(col => col !== analysis.xAxis);
            analysis.recommendations.push(`Y-axis (Values): ${analysis.yAxis.join(', ')}`);
        }

        return analysis;
    }

    isDateString(value) {
        if (typeof value !== 'string') return false;
        
        // Check common date patterns
        const datePatterns = [
            /^\d{4}-\d{2}-\d{2}$/,           // YYYY-MM-DD
            /^\d{4}-\d{2}$/,                 // YYYY-MM
            /^\d{2}\/\d{2}\/\d{4}$/,         // MM/DD/YYYY
            /^\d{4}\/\d{2}\/\d{2}$/,         // YYYY/MM/DD
        ];
        
        return datePatterns.some(pattern => pattern.test(value)) && !isNaN(Date.parse(value));
    }

    displayAxisInformation(axisInfo, chartType) {
        const chartSection = document.getElementById('chart-section');
        let axisInfoDiv = document.getElementById('axis-information');
        
        // Remove existing axis info
        if (axisInfoDiv) {
            axisInfoDiv.remove();
        }

        if (!axisInfo) return;

        // Create new axis information display
        axisInfoDiv = document.createElement('div');
        axisInfoDiv.id = 'axis-information';
        axisInfoDiv.className = 'alert alert-info mb-3';
        
        let content = '<div class="row"><div class="col-md-12">';
        content += '<h6 class="mb-2"><i class="fas fa-info-circle me-2"></i>Chart Configuration:</h6>';
        
        if (chartType === 'pie' || chartType === 'doughnut') {
            content += `<div class="row">`;
            content += `<div class="col-md-6"><strong>Labels:</strong> ${axisInfo.xAxis}</div>`;
            content += `<div class="col-md-6"><strong>Values:</strong> ${axisInfo.yAxis.join(', ')}</div>`;
            content += `</div>`;
        } else {
            content += `<div class="row">`;
            content += `<div class="col-md-6"><strong>X-Axis:</strong> ${axisInfo.xAxis}</div>`;
            content += `<div class="col-md-6"><strong>Y-Axis:</strong> ${axisInfo.yAxis.join(', ')}</div>`;
            content += `</div>`;
            
            // Add data type information
            content += `<div class="row mt-2">`;
            content += `<div class="col-md-6"><small class="text-muted">Data Type: ${axisInfo.dataTypes[axisInfo.xAxis] || 'unknown'}</small></div>`;
            content += `<div class="col-md-6"><small class="text-muted">Data Types: ${axisInfo.yAxis.map(col => axisInfo.dataTypes[col] || 'unknown').join(', ')}</small></div>`;
            content += `</div>`;
        }
        
        // Add recommendations
        if (axisInfo.recommendations.length > 0) {
            content += `<div class="mt-2"><small class="text-muted"><strong>Detected:</strong> ${axisInfo.recommendations.join(' | ')}</small></div>`;
        }
        
        content += '</div></div>';
        axisInfoDiv.innerHTML = content;

        // Insert before the chart type selection
        const chartBody = chartSection.querySelector('.card-body');
        const firstRow = chartBody.querySelector('.row');
        chartBody.insertBefore(axisInfoDiv, firstRow);
    }

    prepareChartData(data, columns, type) {
        if (!data || data.length === 0) return { labels: [], datasets: [] };

        const labels = data.map(row => row[columns[0]]).slice(0, 20); // Limit to 20 items
        const numericColumns = columns.filter(col => 
            data.some(row => typeof row[col] === 'number')
        );

        const datasets = numericColumns.map((col, index) => {
            const values = data.map(row => row[col] || 0).slice(0, 20);
            
            return {
                label: col,
                data: values,
                backgroundColor: this.getChartColors(index, type === 'pie' || type === 'doughnut'),
                borderColor: this.getChartColors(index, false),
                borderWidth: 1
            };
        });

        return { labels, datasets };
    }

    getChartColors(index, multiple = false) {
        const colors = [
            '#0066cc', '#28a745', '#ffc107', '#dc3545', '#6f42c1',
            '#fd7e14', '#20c997', '#6c757d', '#e83e8c', '#17a2b8'
        ];

        if (multiple) {
            return colors.slice(0, 10);
        }
        
        return colors[index % colors.length];
    }

    getChartOptions(type, axisInfo = null) {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === 'pie' || type === 'doughnut',
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y !== undefined ? context.parsed.y : context.parsed;
                            
                            // Format value based on type
                            let formattedValue = value;
                            if (typeof value === 'number') {
                                if (label.toLowerCase().includes('revenue') || 
                                    label.toLowerCase().includes('price') || 
                                    label.toLowerCase().includes('total')) {
                                    formattedValue = new Intl.NumberFormat('en-US', {
                                        style: 'currency',
                                        currency: 'USD'
                                    }).format(value);
                                } else {
                                    formattedValue = new Intl.NumberFormat('en-US').format(value);
                                }
                            }
                            
                            return `${label}: ${formattedValue}`;
                        }
                    }
                }
            }
        };

        if (type === 'line') {
            baseOptions.scales = {
                x: { 
                    grid: { display: false },
                    title: {
                        display: axisInfo && axisInfo.xAxis,
                        text: axisInfo ? axisInfo.xAxis : ''
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: axisInfo && axisInfo.yAxis.length > 0,
                        text: axisInfo ? axisInfo.yAxis.join(' / ') : ''
                    }
                }
            };
        } else if (type === 'bar') {
            baseOptions.scales = {
                x: { 
                    grid: { display: false },
                    title: {
                        display: axisInfo && axisInfo.xAxis,
                        text: axisInfo ? axisInfo.xAxis : ''
                    }
                },
                y: { 
                    beginAtZero: true,
                    title: {
                        display: axisInfo && axisInfo.yAxis.length > 0,
                        text: axisInfo ? axisInfo.yAxis.join(' / ') : ''
                    }
                }
            };
        }

        return baseOptions;
    }

    addToHistory(question, sql) {
        this.queryHistory.unshift({ question, sql, timestamp: new Date() });
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        const container = document.getElementById('query-history');
        container.innerHTML = '';

        this.queryHistory.slice(0, 3).forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'query-history-item';
            historyItem.innerHTML = `
                <div class="query-text">${item.question}</div>
                <div class="query-sql">${item.sql}</div>
                <small class="text-muted">${item.timestamp.toLocaleTimeString()}</small>
            `;
            
            historyItem.addEventListener('click', () => {
                document.getElementById('question-input').value = item.question;
            });
            
            container.appendChild(historyItem);
        });
    }

    exportToCSV() {
        if (!this.currentResults) return;

        const data = this.currentResults.result.data;
        const columns = this.currentResults.result.columns;
        
        let csv = columns.join(',') + '\n';
        
        data.forEach(row => {
            const values = columns.map(col => {
                const value = row[col];
                return typeof value === 'string' ? `"${value}"` : value;
            });
            csv += values.join(',') + '\n';
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'query_results.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    async loadDashboardCharts() {
        // Load predefined dashboard charts
        const chartConfigs = [
            { id: 'sales-trend-chart', type: 'sales_trend', chartType: 'line' },
            { id: 'category-chart', type: 'category_sales', chartType: 'doughnut' },
            { id: 'top-products-chart', type: 'top_products', chartType: 'bar' },
            { id: 'customer-chart', type: 'customer_distribution', chartType: 'bar' }
        ];

        for (const config of chartConfigs) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/charts/data`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chart_type: config.type })
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.chart_data.length > 0) {
                        this.createDashboardChart(config.id, data.chart_data, config.chartType);
                    }
                }
            } catch (error) {
                console.error(`Failed to load ${config.type} chart:`, error);
            }
        }
    }

    createDashboardChart(canvasId, data, type) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const columns = Object.keys(data[0]);
        const axisInfo = this.analyzeDataForVisualization(data, columns, type);
        const chartData = this.prepareChartData(data, columns, type);
        
        new Chart(ctx, {
            type: type,
            data: chartData,
            options: {
                ...this.getChartOptions(type, axisInfo),
                plugins: {
                    ...this.getChartOptions(type, axisInfo).plugins,
                    legend: {
                        display: type === 'doughnut',
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: this.getChartTitle(canvasId, axisInfo)
                    }
                }
            }
        });
    }

    getChartTitle(canvasId, axisInfo) {
        const titles = {
            'sales-trend-chart': 'Sales Trend Over Time',
            'category-chart': 'Revenue by Product Category', 
            'top-products-chart': 'Top Products by Revenue',
            'customer-chart': 'Customer Distribution by City'
        };
        
        let title = titles[canvasId] || 'Chart';
        
        if (axisInfo && axisInfo.xAxis && axisInfo.yAxis.length > 0) {
            title += ` (${axisInfo.yAxis.join(', ')} by ${axisInfo.xAxis})`;
        }
        
        return title;
    }

    showLoading(show) {
        const modalElement = document.getElementById('loadingModal');
        const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
        
        if (show) {
            modal.show();
        } else {
            modal.hide();
            // Force hide the modal backdrop
            setTimeout(() => {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                document.body.classList.remove('modal-open');
                document.body.style.removeProperty('overflow');
                document.body.style.removeProperty('padding-right');
            }, 100);
        }
    }

    showError(message, details = null) {
        document.getElementById('error-message').textContent = message;
        
        if (details) {
            document.getElementById('error-code').textContent = JSON.stringify(details, null, 2);
            document.getElementById('error-details').style.display = 'none';
        } else {
            document.getElementById('show-error-details').style.display = 'none';
        }

        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});