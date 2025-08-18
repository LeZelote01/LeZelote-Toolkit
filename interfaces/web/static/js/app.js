/**
 * LeZelote Toolkit - Main JavaScript Application
 * Provides interactive functionality for the web interface
 */

// Main application namespace
const LeZeloteApp = {
    // Configuration
    config: {
        apiBaseUrl: '/api/v1',
        wsUrl: window.location.protocol === 'https:' ? 'wss://' : 'ws://' + window.location.host,
        refreshInterval: 5000
    },

    // Initialize application
    init: function() {
        console.log('LeZelote Toolkit Web Interface - Initializing...');
        
        // Initialize components
        this.initializeWebSocket();
        this.initializeEventHandlers();
        this.initializeTooltips();
        this.loadDashboardData();
        
        console.log('LeZelote Toolkit Web Interface - Ready');
    },

    // WebSocket connection for real-time updates
    initializeWebSocket: function() {
        try {
            this.ws = new WebSocket(this.config.wsUrl + '/ws');
            
            this.ws.onopen = function() {
                console.log('WebSocket connected');
            };
            
            this.ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                LeZeloteApp.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = function() {
                console.log('WebSocket disconnected, attempting reconnect...');
                setTimeout(() => LeZeloteApp.initializeWebSocket(), 5000);
            };
        } catch (error) {
            console.warn('WebSocket not available:', error.message);
        }
    },

    // Handle WebSocket messages
    handleWebSocketMessage: function(data) {
        switch(data.type) {
            case 'scan_progress':
                this.updateScanProgress(data.payload);
                break;
            case 'scan_complete':
                this.handleScanComplete(data.payload);
                break;
            case 'notification':
                this.showNotification(data.payload);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    },

    // Initialize event handlers
    initializeEventHandlers: function() {
        // Navigation
        $(document).on('click', '[data-toggle="ajax-modal"]', this.loadAjaxModal);
        
        // Forms
        $(document).on('submit', '.ajax-form', this.submitAjaxForm);
        
        // Scan controls
        $(document).on('click', '.start-scan', this.startScan);
        $(document).on('click', '.stop-scan', this.stopScan);
        
        // Project management
        $(document).on('click', '.load-project', this.loadProject);
        
        // Auto-refresh for tables
        setInterval(() => this.refreshDataTables(), this.config.refreshInterval);
    },

    // Initialize Bootstrap tooltips
    initializeTooltips: function() {
        $('[data-toggle="tooltip"]').tooltip();
    },

    // Load dashboard data
    loadDashboardData: function() {
        this.makeApiCall('/dashboard/stats', 'GET')
            .then(data => {
                this.updateDashboardStats(data);
            })
            .catch(error => {
                console.error('Failed to load dashboard data:', error);
            });
    },

    // Update dashboard statistics
    updateDashboardStats: function(stats) {
        if (stats.active_scans !== undefined) {
            $('#active-scans-count').text(stats.active_scans);
        }
        if (stats.total_projects !== undefined) {
            $('#total-projects-count').text(stats.total_projects);
        }
        if (stats.recent_findings !== undefined) {
            $('#recent-findings-count').text(stats.recent_findings);
        }
    },

    // Make API calls
    makeApiCall: function(endpoint, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        return fetch(this.config.apiBaseUrl + endpoint, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
    },

    // Load AJAX modal
    loadAjaxModal: function(event) {
        event.preventDefault();
        
        const url = $(this).attr('href');
        const modalTitle = $(this).data('title') || 'Loading...';
        
        // Create modal HTML
        const modalHtml = `
            <div class="modal fade" id="ajaxModal" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${modalTitle}</h5>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div class="text-center">
                                <i class="fas fa-spinner fa-spin fa-2x"></i>
                                <p class="mt-2">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        $('#ajaxModal').remove();
        
        // Add new modal
        $('body').append(modalHtml);
        
        // Show modal
        $('#ajaxModal').modal('show');
        
        // Load content
        fetch(url)
            .then(response => response.text())
            .then(html => {
                $('#ajaxModal .modal-body').html(html);
            })
            .catch(error => {
                $('#ajaxModal .modal-body').html(`
                    <div class="alert alert-danger">
                        <strong>Error:</strong> Failed to load content.
                    </div>
                `);
            });
    },

    // Submit AJAX form
    submitAjaxForm: function(event) {
        event.preventDefault();
        
        const $form = $(this);
        const url = $form.attr('action');
        const method = $form.attr('method') || 'POST';
        const formData = new FormData(this);
        
        // Show loading state
        const $submitBtn = $form.find('[type="submit"]');
        const originalText = $submitBtn.text();
        $submitBtn.prop('disabled', true).text('Processing...');
        
        fetch(url, {
            method: method,
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                LeZeloteApp.showNotification({
                    type: 'success',
                    message: data.message || 'Operation completed successfully'
                });
                
                // Close modal if form is in modal
                if ($form.closest('.modal').length) {
                    $form.closest('.modal').modal('hide');
                }
                
                // Refresh page or redirect
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.location.reload();
                }
            } else {
                LeZeloteApp.showNotification({
                    type: 'error',
                    message: data.message || 'Operation failed'
                });
            }
        })
        .catch(error => {
            LeZeloteApp.showNotification({
                type: 'error',
                message: 'Network error occurred'
            });
        })
        .finally(() => {
            $submitBtn.prop('disabled', false).text(originalText);
        });
    },

    // Start scan
    startScan: function(event) {
        event.preventDefault();
        
        const scanType = $(this).data('scan-type');
        const projectId = $(this).data('project-id');
        
        LeZeloteApp.makeApiCall('/scans/start', 'POST', {
            scan_type: scanType,
            project_id: projectId
        })
        .then(data => {
            LeZeloteApp.showNotification({
                type: 'success',
                message: 'Scan started successfully'
            });
            // Update UI to show running scan
            LeZeloteApp.refreshScanStatus();
        })
        .catch(error => {
            LeZeloteApp.showNotification({
                type: 'error',
                message: 'Failed to start scan: ' + error.message
            });
        });
    },

    // Stop scan
    stopScan: function(event) {
        event.preventDefault();
        
        const scanId = $(this).data('scan-id');
        
        LeZeloteApp.makeApiCall('/scans/' + scanId + '/stop', 'POST')
        .then(data => {
            LeZeloteApp.showNotification({
                type: 'info',
                message: 'Scan stopped successfully'
            });
            LeZeloteApp.refreshScanStatus();
        })
        .catch(error => {
            LeZeloteApp.showNotification({
                type: 'error',
                message: 'Failed to stop scan: ' + error.message
            });
        });
    },

    // Update scan progress
    updateScanProgress: function(data) {
        const $progressBar = $('#scan-progress-' + data.scan_id);
        if ($progressBar.length) {
            $progressBar.css('width', data.progress + '%');
            $progressBar.text(data.progress + '%');
        }
    },

    // Handle scan completion
    handleScanComplete: function(data) {
        this.showNotification({
            type: 'success',
            message: `Scan completed: ${data.scan_type}`
        });
        this.refreshScanStatus();
    },

    // Refresh scan status
    refreshScanStatus: function() {
        this.makeApiCall('/scans/status', 'GET')
            .then(data => {
                // Update scan status display
                this.updateScanStatusDisplay(data);
            })
            .catch(error => {
                console.error('Failed to refresh scan status:', error);
            });
    },

    // Update scan status display
    updateScanStatusDisplay: function(scans) {
        const $container = $('#scan-status-container');
        if ($container.length) {
            // Update scan status table or cards
            // Implementation depends on UI structure
        }
    },

    // Load project
    loadProject: function(event) {
        event.preventDefault();
        
        const projectId = $(this).data('project-id');
        
        LeZeloteApp.makeApiCall('/projects/' + projectId, 'GET')
            .then(data => {
                // Update project display
                LeZeloteApp.updateProjectDisplay(data);
            })
            .catch(error => {
                LeZeloteApp.showNotification({
                    type: 'error',
                    message: 'Failed to load project: ' + error.message
                });
            });
    },

    // Update project display
    updateProjectDisplay: function(project) {
        $('#current-project-name').text(project.name);
        $('#current-project-status').text(project.status);
        // Update other project-related UI elements
    },

    // Refresh data tables
    refreshDataTables: function() {
        $('.data-table').each(function() {
            if ($(this).hasClass('auto-refresh')) {
                // Refresh DataTable if using DataTables plugin
                if ($.fn.DataTable && $.fn.DataTable.isDataTable(this)) {
                    $(this).DataTable().ajax.reload(null, false);
                }
            }
        });
    },

    // Show notification
    showNotification: function(notification) {
        const types = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        };
        
        const alertClass = types[notification.type] || 'alert-info';
        const icon = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        }[notification.type] || 'fa-info-circle';
        
        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
                <i class="fas ${icon} mr-2"></i>
                ${notification.message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `;
        
        $('body').append(alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            $('.alert').not(':last').fadeOut();
        }, 5000);
    },

    // Utility functions
    utils: {
        // Format file size
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        // Format duration
        formatDuration: function(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            
            if (hours > 0) {
                return `${hours}h ${minutes}m ${secs}s`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        },

        // Escape HTML
        escapeHtml: function(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }
};

// Initialize when DOM is ready
$(document).ready(function() {
    LeZeloteApp.init();
});

// Export for global access
window.LeZeloteApp = LeZeloteApp;