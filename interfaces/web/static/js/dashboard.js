/**
 * Dashboard Specific JavaScript
 * ============================
 * 
 * Dashboard functionality, charts, and real-time updates
 */

(function() {
    'use strict';

    let performanceChart = null;
    let chartData = {
        labels: [],
        cpu: [],
        memory: [],
        disk: []
    };

    const maxDataPoints = 20; // Keep last 20 data points

    /**
     * Initialize dashboard
     */
    function initializeDashboard() {
        console.log('Initializing dashboard...');
        
        // Initialize performance chart
        initializePerformanceChart();
        
        // Set up real-time updates
        initializeRealTimeUpdates();
        
        // Set up new scan modal
        setupNewScanModal();
        
        // Load initial data
        loadInitialData();
        
        console.log('Dashboard initialized');
    }

    /**
     * Initialize performance chart
     */
    function initializePerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;

        const config = {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'CPU %',
                        data: chartData.cpu,
                        borderColor: PentestApp.config.chartColors.primary,
                        backgroundColor: PentestApp.config.chartColors.primary + '20',
                        fill: false,
                        tension: 0.4,
                        pointRadius: 2,
                        pointHoverRadius: 4
                    },
                    {
                        label: 'Memory %',
                        data: chartData.memory,
                        borderColor: PentestApp.config.chartColors.success,
                        backgroundColor: PentestApp.config.chartColors.success + '20',
                        fill: false,
                        tension: 0.4,
                        pointRadius: 2,
                        pointHoverRadius: 4
                    },
                    {
                        label: 'Disk %',
                        data: chartData.disk,
                        borderColor: PentestApp.config.chartColors.warning,
                        backgroundColor: PentestApp.config.chartColors.warning + '20',
                        fill: false,
                        tension: 0.4,
                        pointRadius: 2,
                        pointHoverRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            maxTicksLimit: 10,
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Usage %',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 25,
                            font: {
                                size: 10
                            },
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        }
                    }
                },
                elements: {
                    line: {
                        borderWidth: 2
                    },
                    point: {
                        borderWidth: 1,
                        hoverBorderWidth: 2
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        };

        performanceChart = new Chart(ctx, config);
    }

    /**
     * Update performance chart with new data
     */
    function updatePerformanceChart(data) {
        if (!performanceChart || !data) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });

        // Add new data point
        chartData.labels.push(timeLabel);
        chartData.cpu.push(data.cpu_percent || 0);
        chartData.memory.push(data.memory_percent || 0);
        chartData.disk.push(data.disk_usage || 0);

        // Keep only last N data points
        if (chartData.labels.length > maxDataPoints) {
            chartData.labels.shift();
            chartData.cpu.shift();
            chartData.memory.shift();
            chartData.disk.shift();
        }

        // Update chart
        performanceChart.update('none'); // No animation for real-time updates
    }

    /**
     * Initialize real-time updates
     */
    function initializeRealTimeUpdates() {
        // Update system stats every 30 seconds
        setInterval(fetchSystemStats, 30000);
        
        // Update active scans every 15 seconds
        setInterval(fetchActiveScans, 15000);
        
        // Update activity feed every 60 seconds
        setInterval(fetchRecentActivity, 60000);
    }

    /**
     * Load initial dashboard data
     */
    function loadInitialData() {
        fetchSystemStats();
        fetchActiveScans();
        fetchRecentActivity();
        fetchThreatLevels();
    }

    /**
     * Fetch system statistics
     */
    function fetchSystemStats() {
        PentestApp.api.getSystemStats()
            .then(data => {
                if (data) {
                    updateSystemMetrics(data);
                    updatePerformanceChart(data);
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
        PentestApp.api.getActiveScans()
            .then(data => {
                if (data && data.active_scans) {
                    updateActiveScansList(data.active_scans);
                    updateActiveScansCounter(data.count || data.active_scans.length);
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
        // This would typically fetch from an API endpoint
        // For now, we'll simulate with local data
        const mockActivity = [
            {
                type: 'scan_completed',
                title: 'Scan Completed',
                description: 'Network scan on 192.168.1.0/24',
                timestamp: new Date().toISOString()
            }
        ];

        updateActivityFeed(mockActivity);
    }

    /**
     * Fetch threat levels
     */
    function fetchThreatLevels() {
        // Mock threat level data
        const threatLevels = {
            critical: 2,
            high: 5,
            medium: 12,
            low: 8
        };

        updateThreatLevels(threatLevels);
    }

    /**
     * Update system metrics
     */
    function updateSystemMetrics(data) {
        // CPU Usage
        const cpuUsage = document.getElementById('cpuUsage');
        const cpuProgressBar = document.getElementById('cpuProgressBar');
        if (cpuUsage && data.cpu_percent !== undefined) {
            cpuUsage.textContent = Math.round(data.cpu_percent) + '%';
            if (cpuProgressBar) {
                PentestApp.ui.updateProgress(cpuProgressBar, data.cpu_percent);
                
                // Change color based on usage
                cpuProgressBar.className = 'progress-bar';
                if (data.cpu_percent > 80) {
                    cpuProgressBar.classList.add('bg-danger');
                } else if (data.cpu_percent > 60) {
                    cpuProgressBar.classList.add('bg-warning');
                } else {
                    cpuProgressBar.classList.add('bg-primary');
                }
            }
        }

        // Memory Usage
        const memoryUsage = document.getElementById('memoryUsage');
        const memoryProgressBar = document.getElementById('memoryProgressBar');
        if (memoryUsage && data.memory_percent !== undefined) {
            memoryUsage.textContent = Math.round(data.memory_percent) + '%';
            if (memoryProgressBar) {
                PentestApp.ui.updateProgress(memoryProgressBar, data.memory_percent);
                
                memoryProgressBar.className = 'progress-bar';
                if (data.memory_percent > 80) {
                    memoryProgressBar.classList.add('bg-danger');
                } else if (data.memory_percent > 60) {
                    memoryProgressBar.classList.add('bg-warning');
                } else {
                    memoryProgressBar.classList.add('bg-success');
                }
            }
        }

        // Disk Usage
        const diskUsage = document.getElementById('diskUsage');
        const diskProgressBar = document.getElementById('diskProgressBar');
        if (diskUsage && data.disk_usage !== undefined) {
            diskUsage.textContent = Math.round(data.disk_usage) + '%';
            if (diskProgressBar) {
                PentestApp.ui.updateProgress(diskProgressBar, data.disk_usage);
                
                diskProgressBar.className = 'progress-bar';
                if (data.disk_usage > 90) {
                    diskProgressBar.classList.add('bg-danger');
                } else if (data.disk_usage > 75) {
                    diskProgressBar.classList.add('bg-warning');
                } else {
                    diskProgressBar.classList.add('bg-warning');
                }
            }
        }

        // Active Users
        const activeUsers = document.getElementById('activeUsers');
        if (activeUsers && data.connected_users !== undefined) {
            PentestApp.ui.updateCounter(activeUsers, data.connected_users);
        }

        // Update dashboard stats counters
        if (data.scans_completed !== undefined) {
            const element = document.getElementById('completedScansCount');
            if (element) {
                PentestApp.ui.updateCounter(element, data.scans_completed);
            }
        }

        if (data.vulnerabilities_found !== undefined) {
            const element = document.getElementById('vulnerabilitiesCount');
            if (element) {
                PentestApp.ui.updateCounter(element, data.vulnerabilities_found);
            }
        }
    }

    /**
     * Update active scans counter
     */
    function updateActiveScansCounter(count) {
        const activeScansCount = document.getElementById('activeScansCount');
        const activeScansBadge = document.getElementById('activeScansBadge');

        if (activeScansCount) {
            PentestApp.ui.updateCounter(activeScansCount, count);
        }

        if (activeScansBadge) {
            activeScansBadge.textContent = count;
        }
    }

    /**
     * Update active scans list
     */
    function updateActiveScansList(scans) {
        const activeScansList = document.getElementById('activeScansList');
        if (!activeScansList) return;

        if (!scans || scans.length === 0) {
            activeScansList.innerHTML = `
                <tr class="no-data">
                    <td colspan="5" class="text-center py-4">
                        <i class="fas fa-search fa-2x text-muted mb-3"></i>
                        <div class="text-muted">No active scans</div>
                        <button type="button" class="btn btn-sm btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#newScanModal">
                            Start Your First Scan
                        </button>
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        scans.forEach(scan => {
            html += `
                <tr id="scan-row-${scan.id}">
                    <td>
                        <div class="fw-semibold">${PentestApp.utils.sanitizeHTML(scan.target)}</div>
                        <small class="text-muted">${scan.scan_type || 'Unknown'}</small>
                    </td>
                    <td><span class="badge bg-primary">${scan.scan_type || 'Unknown'}</span></td>
                    <td>
                        <div class="scan-progress">
                            <div class="progress mb-1">
                                <div class="progress-bar bg-primary" role="progressbar" 
                                     id="scan-progress-${scan.id}" 
                                     style="width: ${scan.progress || 0}%"></div>
                            </div>
                            <div class="progress-text">${Math.round(scan.progress || 0)}%</div>
                        </div>
                    </td>
                    <td>
                        <span class="scan-status status-${scan.status || 'running'}" id="scan-status-${scan.id}">
                            ${scan.status || 'Running'}
                        </span>
                    </td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="stopScan('${scan.id}')" title="Stop scan">
                            <i class="fas fa-stop"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="viewScanDetails('${scan.id}')" title="View details">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        activeScansList.innerHTML = html;
    }

    /**
     * Update activity feed
     */
    function updateActivityFeed(activities) {
        const activityFeed = document.getElementById('activityFeed');
        if (!activityFeed || !activities) return;

        let html = '';
        activities.forEach(activity => {
            const iconClass = getActivityIcon(activity.type);
            const bgClass = getActivityBgClass(activity.type);

            html += `
                <div class="activity-item">
                    <div class="activity-icon bg-${bgClass}">
                        <i class="fas fa-${iconClass}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${PentestApp.utils.sanitizeHTML(activity.title)}</div>
                        <div class="activity-description">${PentestApp.utils.sanitizeHTML(activity.description)}</div>
                        <div class="activity-time">${PentestApp.utils.formatRelativeTime(activity.timestamp)}</div>
                    </div>
                </div>
            `;
        });

        activityFeed.innerHTML = html;
    }

    /**
     * Update threat levels
     */
    function updateThreatLevels(levels) {
        const total = levels.critical + levels.high + levels.medium + levels.low;
        
        // Update counts
        const criticalCount = document.getElementById('criticalCount');
        const highCount = document.getElementById('highCount');
        const mediumCount = document.getElementById('mediumCount');
        const lowCount = document.getElementById('lowCount');

        if (criticalCount) PentestApp.ui.updateCounter(criticalCount, levels.critical);
        if (highCount) PentestApp.ui.updateCounter(highCount, levels.high);
        if (mediumCount) PentestApp.ui.updateCounter(mediumCount, levels.medium);
        if (lowCount) PentestApp.ui.updateCounter(lowCount, levels.low);

        // Update progress bars
        if (total > 0) {
            const criticalProgress = document.getElementById('criticalProgress');
            const highProgress = document.getElementById('highProgress');
            const mediumProgress = document.getElementById('mediumProgress');
            const lowProgress = document.getElementById('lowProgress');

            if (criticalProgress) PentestApp.ui.updateProgress(criticalProgress, (levels.critical / total) * 100);
            if (highProgress) PentestApp.ui.updateProgress(highProgress, (levels.high / total) * 100);
            if (mediumProgress) PentestApp.ui.updateProgress(mediumProgress, (levels.medium / total) * 100);
            if (lowProgress) PentestApp.ui.updateProgress(lowProgress, (levels.low / total) * 100);
        }

        // Calculate risk score
        const riskScore = (levels.critical * 4) + (levels.high * 3) + (levels.medium * 2) + (levels.low * 1);
        const riskScoreElement = document.getElementById('riskScore');
        if (riskScoreElement) {
            riskScoreElement.textContent = riskScore;
            
            // Update badge color based on risk level
            riskScoreElement.className = 'badge';
            if (riskScore > 20) {
                riskScoreElement.classList.add('bg-danger');
            } else if (riskScore > 10) {
                riskScoreElement.classList.add('bg-warning');
            } else if (riskScore > 5) {
                riskScoreElement.classList.add('bg-info');
            } else {
                riskScoreElement.classList.add('bg-success');
            }
        }
    }

    /**
     * Setup new scan modal
     */
    function setupNewScanModal() {
        const newScanForm = document.getElementById('newScanForm');
        const startScanBtn = document.getElementById('startScanBtn');

        if (!newScanForm || !startScanBtn) return;

        startScanBtn.addEventListener('click', function() {
            const scanTarget = document.getElementById('scanTarget').value.trim();
            const scanType = document.getElementById('scanType').value;
            const scanPorts = document.getElementById('scanPorts').value.trim();
            const scanThreads = document.getElementById('scanThreads').value;
            const scanDescription = document.getElementById('scanDescription').value.trim();
            const saveProject = document.getElementById('saveProject').checked;
            const enableNotifications = document.getElementById('enableNotifications').checked;

            // Validate form
            if (!scanTarget) {
                PentestApp.ui.showToast('Please enter a target', 'error');
                return;
            }

            if (!scanType) {
                PentestApp.ui.showToast('Please select a scan type', 'error');
                return;
            }

            // Validate target format
            if (!isValidTarget(scanTarget)) {
                PentestApp.ui.showToast('Please enter a valid IP address, domain, or network range', 'error');
                return;
            }

            // Prepare scan configuration
            const scanConfig = {
                target: scanTarget,
                type: scanType,
                ports: scanPorts || '1-1000',
                threads: parseInt(scanThreads) || 10,
                description: scanDescription,
                save_project: saveProject,
                notifications: enableNotifications
            };

            // Disable button and show loading
            startScanBtn.disabled = true;
            startScanBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Starting...';

            // Start scan
            PentestApp.api.startScan(scanConfig)
                .then(response => {
                    if (response.success) {
                        PentestApp.ui.showToast('Scan started successfully!', 'success');
                        
                        // Close modal
                        const modal = bootstrap.Modal.getInstance(document.getElementById('newScanModal'));
                        modal.hide();
                        
                        // Reset form
                        newScanForm.reset();
                        
                        // Refresh active scans
                        setTimeout(fetchActiveScans, 1000);
                    } else {
                        PentestApp.ui.showToast(response.message || 'Failed to start scan', 'error');
                    }
                })
                .catch(error => {
                    console.error('Start scan error:', error);
                    PentestApp.ui.showToast('Failed to start scan', 'error');
                })
                .finally(() => {
                    // Reset button
                    startScanBtn.disabled = false;
                    startScanBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Scan';
                });
        });

        // Reset form when modal is closed
        const modal = document.getElementById('newScanModal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function() {
                newScanForm.reset();
                startScanBtn.disabled = false;
                startScanBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Scan';
            });
        }
    }

    /**
     * Validate scan target
     */
    function isValidTarget(target) {
        // Check if it's a valid IP address
        if (PentestApp.utils.isValidIP(target)) {
            return true;
        }

        // Check if it's a valid domain
        if (PentestApp.utils.isValidDomain(target)) {
            return true;
        }

        // Check if it's a valid CIDR range
        const cidrRegex = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;
        if (cidrRegex.test(target)) {
            return true;
        }

        // Check if it's a valid URL
        if (PentestApp.utils.isValidURL(target)) {
            return true;
        }

        return false;
    }

    /**
     * Get activity icon
     */
    function getActivityIcon(type) {
        const icons = {
            'scan_started': 'play',
            'scan_completed': 'check',
            'scan_failed': 'times',
            'vulnerability_found': 'exclamation-triangle',
            'report_generated': 'file-alt',
            'user_login': 'sign-in-alt',
            'user_logout': 'sign-out-alt'
        };
        return icons[type] || 'info';
    }

    /**
     * Get activity background class
     */
    function getActivityBgClass(type) {
        const classes = {
            'scan_started': 'primary',
            'scan_completed': 'success',
            'scan_failed': 'danger',
            'vulnerability_found': 'warning',
            'report_generated': 'info',
            'user_login': 'success',
            'user_logout': 'secondary'
        };
        return classes[type] || 'secondary';
    }

    // ==========================================================================
    // Export functions
    // ==========================================================================

    // Make functions globally available
    window.initializeDashboard = initializeDashboard;
    window.fetchSystemStats = fetchSystemStats;
    window.fetchActiveScans = fetchActiveScans;
    window.fetchRecentActivity = fetchRecentActivity;
    window.updatePerformanceChart = updatePerformanceChart;

})();