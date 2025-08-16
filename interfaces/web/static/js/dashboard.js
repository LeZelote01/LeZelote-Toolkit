/*
 * Dashboard JavaScript for Pentest-USB Toolkit
 * ===========================================
 */

// Dashboard state
let dashboardChart = null;
let refreshTimer = null;

/**
 * Initialize dashboard
 */
function initializeDashboard() {
    console.log('Initializing dashboard...');
    
    // Load initial data
    loadDashboardData();
    
    // Initialize charts
    initializePerformanceChart();
    
    // Setup periodic updates
    startPeriodicUpdates();
    
    // Setup event listeners
    setupDashboardEventListeners();
    
    console.log('Dashboard initialized');
}

/**
 * Load initial dashboard data
 */
function loadDashboardData() {
    // Fetch system statistics
    fetchSystemStats();
    
    // Fetch active scans
    fetchActiveScans();
    
    // Fetch recent activity
    fetchRecentActivity();
    
    // Update date/time
    updateDateTime();
}

/**
 * Fetch system statistics
 */
function fetchSystemStats() {
    makeRequest('/api/system/stats')
        .then(data => {
            if (data.success || data.cpu_percent !== undefined) {
                updateSystemMetrics(data);
                updateStatsBadges(data);
            }
        })
        .catch(error => {
            console.error('Failed to fetch system stats:', error);
        });
}

/**
 * Fetch active scans
 */
function fetchActiveScans() {
    makeRequest('/api/scans/active')
        .then(data => {
            if (data.success) {
                updateActiveScansList(data.active_scans || []);
                updateActiveScansBadge(data.count || 0);
            }
        })
        .catch(error => {
            console.error('Failed to fetch active scans:', error);
        });
}

/**
 * Fetch recent activity
 */
function fetchRecentActivity() {
    // Mock activity data for now
    const mockActivity = [
        {
            type: 'scan_completed',
            title: 'Scan Completed',
            description: 'Network scan on 192.168.1.0/24',
            time: new Date(Date.now() - 2 * 60 * 1000),
            icon: 'fas fa-check',
            color: 'success'
        },
        {
            type: 'vulnerability_found',
            title: 'High Severity Vulnerability',
            description: 'SQL Injection found in login form',
            time: new Date(Date.now() - 15 * 60 * 1000),
            icon: 'fas fa-exclamation-triangle',
            color: 'danger'
        },
        {
            type: 'scan_started',
            title: 'Scan Started',
            description: 'Web application scan on example.com',
            time: new Date(Date.now() - 30 * 60 * 1000),
            icon: 'fas fa-play',
            color: 'primary'
        },
        {
            type: 'report_generated',
            title: 'Report Generated',
            description: 'Executive summary for Project Alpha',
            time: new Date(Date.now() - 2 * 60 * 60 * 1000),
            icon: 'fas fa-file-alt',
            color: 'info'
        }
    ];
    
    updateActivityFeed(mockActivity);
}

/**
 * Initialize performance chart
 */
function initializePerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Destroy existing chart if exists
    if (dashboardChart) {
        dashboardChart.destroy();
    }
    
    const chartData = {
        labels: [],
        datasets: [
            {
                label: 'CPU Usage (%)',
                data: [],
                borderColor: 'rgb(0, 123, 255)',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Memory Usage (%)',
                data: [],
                borderColor: 'rgb(40, 167, 69)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Active Scans',
                data: [],
                borderColor: 'rgb(255, 193, 7)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y1'
            }
        ]
    };
    
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.dataset.yAxisID === 'y1') {
                            label += context.parsed.y;
                        } else {
                            label += context.parsed.y + '%';
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: {
                    display: true,
                    text: 'Usage (%)'
                },
                min: 0,
                max: 100
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                title: {
                    display: true,
                    text: 'Active Scans'
                },
                min: 0,
                grid: {
                    drawOnChartArea: false,
                }
            }
        }
    };
    
    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });
    
    // Initialize with some data points
    initializeChartData();
}

/**
 * Initialize chart with initial data points
 */
function initializeChartData() {
    if (!dashboardChart) return;
    
    const now = new Date();
    const points = 10;
    
    // Generate initial data points
    for (let i = points - 1; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 30000); // 30 second intervals
        const timeLabel = time.toLocaleTimeString();
        
        dashboardChart.data.labels.push(timeLabel);
        dashboardChart.data.datasets[0].data.push(Math.random() * 50 + 20); // CPU
        dashboardChart.data.datasets[1].data.push(Math.random() * 40 + 30); // Memory
        dashboardChart.data.datasets[2].data.push(Math.floor(Math.random() * 5)); // Active scans
    }
    
    dashboardChart.update('none');
}

/**
 * Update chart with new data point
 */
function updatePerformanceChart(cpuPercent, memoryPercent, activeScans) {
    if (!dashboardChart) return;
    
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();
    
    // Add new data point
    dashboardChart.data.labels.push(timeLabel);
    dashboardChart.data.datasets[0].data.push(cpuPercent || 0);
    dashboardChart.data.datasets[1].data.push(memoryPercent || 0);
    dashboardChart.data.datasets[2].data.push(activeScans || 0);
    
    // Remove old data points (keep last 20)
    if (dashboardChart.data.labels.length > 20) {
        dashboardChart.data.labels.shift();
        dashboardChart.data.datasets.forEach(dataset => {
            dataset.data.shift();
        });
    }
    
    dashboardChart.update('none');
}

/**
 * Update activity feed
 */
function updateActivityFeed(activities) {
    const feedContainer = document.getElementById('activityFeed');
    if (!feedContainer) return;
    
    // Clear existing activities
    feedContainer.innerHTML = '';
    
    activities.forEach(activity => {
        const activityItem = createActivityItem(activity);
        feedContainer.appendChild(activityItem);
    });
    
    // Add animation
    feedContainer.classList.add('fade-in');
}

/**
 * Create activity item element
 */
function createActivityItem(activity) {
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    const timeStr = getRelativeTime(activity.time);
    
    item.innerHTML = `
        <div class="activity-icon bg-${activity.color}">
            <i class="${activity.icon}"></i>
        </div>
        <div class="activity-content">
            <div class="activity-title">${escapeHtml(activity.title)}</div>
            <div class="activity-description">${escapeHtml(activity.description)}</div>
            <div class="activity-time">${timeStr}</div>
        </div>
    `;
    
    return item;
}

/**
 * Setup dashboard event listeners
 */
function setupDashboardEventListeners() {
    // New scan modal setup
    setupNewScanModal();
    
    // Chart toggle functionality
    setupChartToggle();
    
    // Activity refresh
    const refreshActivityBtn = document.querySelector('[onclick="refreshActivity()"]');
    if (refreshActivityBtn) {
        refreshActivityBtn.addEventListener('click', function(e) {
            e.preventDefault();
            fetchRecentActivity();
            showToast('Activity feed refreshed', 'info', 2000);
        });
    }
    
    // Dashboard refresh
    const refreshDashboardBtn = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshDashboardBtn) {
        refreshDashboardBtn.addEventListener('click', function(e) {
            e.preventDefault();
            refreshDashboard();
        });
    }
    
    // WebSocket event listeners
    document.addEventListener('systemStatsReceived', function(e) {
        updatePerformanceChart(
            e.detail.cpu_percent,
            e.detail.memory_percent,
            e.detail.active_scans
        );
    });
    
    document.addEventListener('activeScansReceived', function(e) {
        updateActiveScansList(e.detail);
    });
    
    document.addEventListener('scanCompleted', function(e) {
        // Refresh activity feed when scan completes
        setTimeout(fetchRecentActivity, 1000);
    });
}

/**
 * Setup new scan modal
 */
function setupNewScanModal() {
    const modal = document.getElementById('newScanModal');
    const form = document.getElementById('newScanForm');
    const startBtn = document.getElementById('startScanBtn');
    
    if (!modal || !form || !startBtn) return;
    
    startBtn.addEventListener('click', function() {
        const formData = new FormData(form);
        
        // Validate form
        if (!formData.get('target') || !formData.get('scan_type')) {
            showToast('Please fill in all required fields', 'error');
            return;
        }
        
        // Show loading state
        startBtn.disabled = true;
        startBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Starting...';
        
        // Submit scan request
        const scanData = {
            target: formData.get('target'),
            type: formData.get('scan_type'),
            ports: formData.get('ports') || '1-1000',
            threads: parseInt(formData.get('threads')) || 10,
            description: formData.get('description') || '',
            save_project: formData.get('save_project') === 'on',
            notifications: formData.get('notifications') === 'on'
        };
        
        makeRequest('/scan/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scanData)
        })
        .then(response => {
            if (response.success) {
                showToast('Scan started successfully!', 'success');
                
                // Close modal
                bootstrap.Modal.getInstance(modal).hide();
                
                // Reset form
                form.reset();
                
                // Refresh active scans
                setTimeout(fetchActiveScans, 1000);
            } else {
                throw new Error(response.message || 'Failed to start scan');
            }
        })
        .catch(error => {
            console.error('Scan start error:', error);
            showToast(error.message || 'Failed to start scan', 'error');
        })
        .finally(() => {
            // Reset button state
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Scan';
        });
    });
    
    // Reset form when modal is closed
    modal.addEventListener('hidden.bs.modal', function() {
        form.reset();
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Scan';
    });
}

/**
 * Setup chart toggle functionality
 */
function setupChartToggle() {
    const toggleBtn = document.querySelector('[onclick="toggleMetricsView()"]');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const chartContainer = document.querySelector('.chart-container');
            if (chartContainer) {
                chartContainer.classList.toggle('expanded');
                
                if (chartContainer.classList.contains('expanded')) {
                    chartContainer.style.height = '400px';
                } else {
                    chartContainer.style.height = '300px';
                }
                
                // Resize chart
                if (dashboardChart) {
                    setTimeout(() => {
                        dashboardChart.resize();
                    }, 300);
                }
            }
        });
    }
}

/**
 * Start periodic updates
 */
function startPeriodicUpdates() {
    // Update every 30 seconds
    refreshTimer = setInterval(() => {
        fetchSystemStats();
        fetchActiveScans();
        updateDateTime();
    }, 30000);
    
    // Update activity every 2 minutes
    setInterval(fetchRecentActivity, 120000);
}

/**
 * Stop periodic updates
 */
function stopPeriodicUpdates() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

/**
 * Refresh dashboard data
 */
function refreshDashboard() {
    loadDashboardData();
    showToast('Dashboard refreshed', 'success', 2000);
}

/**
 * Update current date/time display
 */
function updateDateTime() {
    const dateTimeElement = document.getElementById('currentDateTime');
    if (dateTimeElement) {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        dateTimeElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

/**
 * View scan details
 */
function viewScanDetails(scanId) {
    // Navigate to scan details or show modal
    window.location.href = `/scan/monitor/${scanId}`;
}

/**
 * Stop scan
 */
function stopScan(scanId) {
    showConfirmation(
        'Are you sure you want to stop this scan?',
        function() {
            makeRequest(`/scan/api/stop/${scanId}`, {
                method: 'POST'
            })
            .then(response => {
                if (response.success) {
                    showToast('Scan stopped successfully', 'success');
                    fetchActiveScans(); // Refresh the list
                } else {
                    throw new Error(response.message || 'Failed to stop scan');
                }
            })
            .catch(error => {
                console.error('Stop scan error:', error);
                showToast(error.message || 'Failed to stop scan', 'error');
            });
        },
        'Stop Scan'
    );
}

/**
 * Page-specific refresh function
 */
function refreshPageData() {
    refreshDashboard();
}

/**
 * Clean up when leaving page
 */
function cleanupDashboard() {
    stopPeriodicUpdates();
    
    if (dashboardChart) {
        dashboardChart.destroy();
        dashboardChart = null;
    }
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopPeriodicUpdates();
    } else {
        startPeriodicUpdates();
        refreshDashboard();
    }
});

// Clean up when leaving page
window.addEventListener('beforeunload', cleanupDashboard);

// Expose functions globally
window.dashboard = {
    initialize: initializeDashboard,
    refresh: refreshDashboard,
    cleanup: cleanupDashboard,
    viewScanDetails: viewScanDetails,
    stopScan: stopScan
};

window.viewScanDetails = viewScanDetails;
window.stopScan = stopScan;