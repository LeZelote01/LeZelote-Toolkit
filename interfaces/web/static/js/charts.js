/*
 * Chart.js Integration for Pentest-USB Toolkit Web Interface
 * ========================================================== 
 */

// Chart configuration and management
window.ChartManager = {
    charts: {},
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                intersect: false,
                mode: 'index',
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0,0,0,0.1)',
                },
                ticks: {
                    color: '#6c757d',
                }
            },
            x: {
                grid: {
                    color: 'rgba(0,0,0,0.1)',
                },
                ticks: {
                    color: '#6c757d',
                }
            }
        }
    },
    colors: {
        primary: '#007bff',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        secondary: '#6c757d',
        light: '#f8f9fa',
        dark: '#343a40'
    }
};

/**
 * Initialize all charts on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

/**
 * Initialize charts based on canvas elements found on page
 */
function initializeCharts() {
    // Vulnerability Severity Distribution
    const vulnSeverityCanvas = document.getElementById('vulnSeverityChart');
    if (vulnSeverityCanvas) {
        createVulnerabilitySeverityChart(vulnSeverityCanvas);
    }
    
    // Scan Timeline Chart
    const scanTimelineCanvas = document.getElementById('scanTimelineChart');
    if (scanTimelineCanvas) {
        createScanTimelineChart(scanTimelineCanvas);
    }
    
    // CVSS Score Distribution
    const cvssScoreCanvas = document.getElementById('cvssScoreChart');
    if (cvssScoreCanvas) {
        createCVSSDistributionChart(cvssScoreCanvas);
    }
    
    // Risk Assessment Radar
    const riskRadarCanvas = document.getElementById('riskRadarChart');
    if (riskRadarCanvas) {
        createRiskAssessmentRadar(riskRadarCanvas);
    }
    
    // Scan Progress Chart
    const scanProgressCanvas = document.getElementById('scanProgressChart');
    if (scanProgressCanvas) {
        createScanProgressChart(scanProgressCanvas);
    }
    
    // Vulnerability Trends Chart
    const vulnTrendsCanvas = document.getElementById('vulnTrendsChart');
    if (vulnTrendsCanvas) {
        createVulnerabilityTrendsChart(vulnTrendsCanvas);
    }
    
    // Asset Coverage Chart
    const assetCoverageCanvas = document.getElementById('assetCoverageChart');
    if (assetCoverageCanvas) {
        createAssetCoverageChart(assetCoverageCanvas);
    }
    
    // Compliance Status Chart
    const complianceCanvas = document.getElementById('complianceChart');
    if (complianceCanvas) {
        createComplianceChart(complianceCanvas);
    }
    
    // System Performance Chart
    const perfCanvas = document.getElementById('performanceChart');
    if (perfCanvas) {
        createPerformanceChart(perfCanvas);
    }
}

/**
 * Create vulnerability severity distribution pie chart
 */
function createVulnerabilitySeverityChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Get data from data attributes or use sample data
    const data = JSON.parse(canvas.dataset.chartData || '{"critical": 5, "high": 12, "medium": 18, "low": 25, "info": 8}');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
            datasets: [{
                data: [data.critical, data.high, data.medium, data.low, data.info],
                backgroundColor: [
                    ChartManager.colors.danger,
                    ChartManager.colors.warning,
                    ChartManager.colors.info,
                    ChartManager.colors.success,
                    ChartManager.colors.secondary
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverBorderWidth: 4
            }]
        },
        options: {
            ...ChartManager.defaultOptions,
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    ChartManager.charts.vulnSeverity = chart;
    return chart;
}

/**
 * Create scan timeline chart
 */
function createScanTimelineChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Sample data - replace with real data
    const data = JSON.parse(canvas.dataset.chartData || '{"labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "scans": [12, 19, 8, 15, 22, 11, 6], "vulnerabilities": [45, 78, 32, 65, 89, 44, 23]}');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Scans Completed',
                    data: data.scans,
                    borderColor: ChartManager.colors.primary,
                    backgroundColor: ChartManager.colors.primary + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: ChartManager.colors.primary,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                },
                {
                    label: 'Vulnerabilities Found',
                    data: data.vulnerabilities,
                    borderColor: ChartManager.colors.danger,
                    backgroundColor: ChartManager.colors.danger + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: ChartManager.colors.danger,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }
            ]
        },
        options: {
            ...ChartManager.defaultOptions,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: ChartManager.colors.primary,
                    borderWidth: 1
                }
            }
        }
    });
    
    ChartManager.charts.scanTimeline = chart;
    return chart;
}

/**
 * Create CVSS score distribution histogram
 */
function createCVSSDistributionChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = JSON.parse(canvas.dataset.chartData || '{"scores": [2, 8, 15, 12, 18, 22, 16, 10, 5, 3]}');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10'],
            datasets: [{
                label: 'Number of Vulnerabilities',
                data: data.scores,
                backgroundColor: [
                    ChartManager.colors.success,
                    ChartManager.colors.success,
                    ChartManager.colors.success,
                    ChartManager.colors.info,
                    ChartManager.colors.info,
                    ChartManager.colors.warning,
                    ChartManager.colors.warning,
                    ChartManager.colors.danger,
                    ChartManager.colors.danger,
                    ChartManager.colors.danger
                ],
                borderColor: '#ffffff',
                borderWidth: 1
            }]
        },
        options: {
            ...ChartManager.defaultOptions,
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'CVSS Score Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `CVSS Range: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `Vulnerabilities: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'CVSS Score Range'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Vulnerabilities'
                    },
                    beginAtZero: true
                }
            }
        }
    });
    
    ChartManager.charts.cvssDistribution = chart;
    return chart;
}

/**
 * Create risk assessment radar chart
 */
function createRiskAssessmentRadar(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = JSON.parse(canvas.dataset.chartData || '{"current": [65, 80, 45, 70, 55, 85], "target": [85, 95, 80, 90, 85, 95]}');
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Network Security', 'Web Applications', 'Data Protection', 'Access Control', 'Monitoring', 'Compliance'],
            datasets: [
                {
                    label: 'Current Security Level',
                    data: data.current,
                    borderColor: ChartManager.colors.danger,
                    backgroundColor: ChartManager.colors.danger + '30',
                    pointBackgroundColor: ChartManager.colors.danger,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    borderWidth: 2
                },
                {
                    label: 'Target Security Level',
                    data: data.target,
                    borderColor: ChartManager.colors.success,
                    backgroundColor: ChartManager.colors.success + '30',
                    pointBackgroundColor: ChartManager.colors.success,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    borderWidth: 2
                }
            ]
        },
        options: {
            ...ChartManager.defaultOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        color: '#6c757d'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.r}%`;
                        }
                    }
                }
            }
        }
    });
    
    ChartManager.charts.riskRadar = chart;
    return chart;
}

/**
 * Create real-time scan progress chart
 */
function createScanProgressChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Scan Progress (%)',
                data: [],
                borderColor: ChartManager.colors.primary,
                backgroundColor: ChartManager.colors.primary + '20',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...ChartManager.defaultOptions,
            animation: {
                duration: 0 // Disable animation for real-time updates
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second',
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Progress (%)'
                    }
                }
            },
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                legend: {
                    display: false
                }
            }
        }
    });
    
    ChartManager.charts.scanProgress = chart;
    return chart;
}

/**
 * Create vulnerability trends over time chart
 */
function createVulnerabilityTrendsChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = JSON.parse(canvas.dataset.chartData || '{"labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "critical": [2, 1, 3, 1, 2, 0], "high": [5, 8, 4, 6, 3, 2], "medium": [12, 15, 18, 14, 16, 11], "low": [20, 25, 22, 28, 24, 19]}');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Critical',
                    data: data.critical,
                    backgroundColor: ChartManager.colors.danger,
                    stack: 'Stack 0'
                },
                {
                    label: 'High',
                    data: data.high,
                    backgroundColor: ChartManager.colors.warning,
                    stack: 'Stack 0'
                },
                {
                    label: 'Medium',
                    data: data.medium,
                    backgroundColor: ChartManager.colors.info,
                    stack: 'Stack 0'
                },
                {
                    label: 'Low',
                    data: data.low,
                    backgroundColor: ChartManager.colors.success,
                    stack: 'Stack 0'
                }
            ]
        },
        options: {
            ...ChartManager.defaultOptions,
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Vulnerability Trends Over Time'
                }
            },
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Number of Vulnerabilities'
                    }
                }
            }
        }
    });
    
    ChartManager.charts.vulnTrends = chart;
    return chart;
}

/**
 * Create asset coverage chart
 */
function createAssetCoverageChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = JSON.parse(canvas.dataset.chartData || '{"scanned": 85, "unscanned": 15}');
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Scanned Assets', 'Unscanned Assets'],
            datasets: [{
                data: [data.scanned, data.unscanned],
                backgroundColor: [ChartManager.colors.success, ChartManager.colors.secondary],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            ...ChartManager.defaultOptions,
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Asset Scan Coverage',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const percentage = context.parsed;
                            return `${context.label}: ${percentage}%`;
                        }
                    }
                }
            }
        }
    });
    
    ChartManager.charts.assetCoverage = chart;
    return chart;
}

/**
 * Create compliance status chart
 */
function createComplianceChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const data = JSON.parse(canvas.dataset.chartData || '{"frameworks": ["PCI-DSS", "HIPAA", "GDPR", "SOX", "ISO 27001"], "compliance": [85, 92, 78, 88, 91]}');
    
    const chart = new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: data.frameworks,
            datasets: [{
                label: 'Compliance Percentage',
                data: data.compliance,
                backgroundColor: data.compliance.map(score => {
                    if (score >= 90) return ChartManager.colors.success;
                    if (score >= 70) return ChartManager.colors.warning;
                    return ChartManager.colors.danger;
                }),
                borderWidth: 1,
                borderColor: '#ffffff'
            }]
        },
        options: {
            indexAxis: 'y',
            ...ChartManager.defaultOptions,
            plugins: {
                ...ChartManager.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Compliance Status by Framework'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.x}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Compliance Percentage'
                    }
                }
            }
        }
    });
    
    ChartManager.charts.compliance = chart;
    return chart;
}

/**
 * Create system performance monitoring chart
 */
function createPerformanceChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU Usage (%)',
                    data: [],
                    borderColor: ChartManager.colors.primary,
                    backgroundColor: ChartManager.colors.primary + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Memory Usage (%)',
                    data: [],
                    borderColor: ChartManager.colors.success,
                    backgroundColor: ChartManager.colors.success + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Disk Usage (%)',
                    data: [],
                    borderColor: ChartManager.colors.warning,
                    backgroundColor: ChartManager.colors.warning + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            ...ChartManager.defaultOptions,
            animation: {
                duration: 0
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Usage (%)'
                    }
                }
            }
        }
    });
    
    ChartManager.charts.performance = chart;
    return chart;
}

/**
 * Update scan progress chart with new data point
 */
function updateScanProgressChart(progress, timestamp) {
    const chart = ChartManager.charts.scanProgress;
    if (!chart) return;
    
    const data = chart.data;
    data.labels.push(timestamp || new Date());
    data.datasets[0].data.push(progress);
    
    // Keep only last 50 data points
    if (data.labels.length > 50) {
        data.labels.shift();
        data.datasets[0].data.shift();
    }
    
    chart.update('none');
}

/**
 * Update performance chart with system stats
 */
function updatePerformanceChart(stats) {
    const chart = ChartManager.charts.performance;
    if (!chart) return;
    
    const data = chart.data;
    const timestamp = new Date();
    
    data.labels.push(timestamp);
    data.datasets[0].data.push(stats.cpu_percent || 0);
    data.datasets[1].data.push(stats.memory_percent || 0);
    data.datasets[2].data.push(stats.disk_usage || 0);
    
    // Keep only last 20 data points (10 minutes at 30-second intervals)
    if (data.labels.length > 20) {
        data.labels.shift();
        data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    chart.update('none');
}

/**
 * Update vulnerability severity chart
 */
function updateVulnerabilitySeverityChart(severityData) {
    const chart = ChartManager.charts.vulnSeverity;
    if (!chart) return;
    
    chart.data.datasets[0].data = [
        severityData.critical || 0,
        severityData.high || 0,
        severityData.medium || 0,
        severityData.low || 0,
        severityData.info || 0
    ];
    
    chart.update();
}

/**
 * Destroy all charts (cleanup)
 */
function destroyAllCharts() {
    Object.values(ChartManager.charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    ChartManager.charts = {};
}

/**
 * Resize all charts (useful for responsive design)
 */
function resizeAllCharts() {
    Object.values(ChartManager.charts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}

/**
 * Export chart as image
 */
function exportChart(chartId, filename) {
    const chart = ChartManager.charts[chartId];
    if (!chart) {
        console.error(`Chart ${chartId} not found`);
        return;
    }
    
    const url = chart.toBase64Image();
    const link = document.createElement('a');
    link.download = filename || `${chartId}_chart.png`;
    link.href = url;
    link.click();
}

/**
 * Listen for system stats updates and update charts
 */
document.addEventListener('systemStatsUpdated', function(event) {
    updatePerformanceChart(event.detail);
});

/**
 * Listen for scan progress updates
 */
document.addEventListener('scanProgressUpdated', function(event) {
    const { scanId, progress } = event.detail;
    updateScanProgressChart(progress);
});

/**
 * Listen for vulnerability updates
 */
document.addEventListener('vulnerabilityDataUpdated', function(event) {
    updateVulnerabilitySeverityChart(event.detail);
});

// Resize charts on window resize
window.addEventListener('resize', function() {
    setTimeout(resizeAllCharts, 100);
});

// Export functions to global scope
window.ChartManager.updateScanProgress = updateScanProgressChart;
window.ChartManager.updatePerformance = updatePerformanceChart;
window.ChartManager.updateVulnerabilities = updateVulnerabilitySeverityChart;
window.ChartManager.destroy = destroyAllCharts;
window.ChartManager.resize = resizeAllCharts;
window.ChartManager.export = exportChart;