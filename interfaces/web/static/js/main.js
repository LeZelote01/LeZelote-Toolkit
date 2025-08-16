/**
 * Main JavaScript for Pentest-USB Toolkit Web Interface
 * =====================================================
 * 
 * Core functionality, utilities, and initialization
 */

(function() {
    'use strict';

    // Global app object
    window.PentestApp = {
        // Configuration
        config: {
            apiBaseUrl: '/api',
            wsNamespace: '/',
            updateInterval: 30000, // 30 seconds
            toastDuration: 5000,
            chartColors: {
                primary: '#2563eb',
                success: '#059669', 
                warning: '#d97706',
                danger: '#dc2626',
                info: '#0891b2'
            }
        },
        
        // State management
        state: {
            authenticated: false,
            user: null,
            activeScans: {},
            systemStats: {},
            notifications: []
        },
        
        // Utility functions
        utils: {},
        
        // API client
        api: {},
        
        // UI components
        ui: {},
        
        // WebSocket connection
        ws: null
    };

    // ==========================================================================
    // Utility Functions
    // ==========================================================================
    
    PentestApp.utils = {
        
        /**
         * Format bytes to human readable format
         */
        formatBytes: function(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        },
        
        /**
         * Format duration in seconds to human readable format
         */
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
        
        /**
         * Format timestamp to relative time
         */
        formatRelativeTime: function(timestamp) {
            const now = new Date();
            const date = new Date(timestamp);
            const diff = Math.floor((now - date) / 1000);
            
            if (diff < 60) return 'Just now';
            if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
            if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
            
            return date.toLocaleDateString();
        },
        
        /**
         * Debounce function execution
         */
        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction() {
                const context = this;
                const args = arguments;
                
                const later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                
                if (callNow) func.apply(context, args);
            };
        },
        
        /**
         * Throttle function execution
         */
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            }
        },
        
        /**
         * Generate random ID
         */
        generateId: function(prefix = 'id') {
            return prefix + '_' + Math.random().toString(36).substr(2, 9);
        },
        
        /**
         * Validate IP address
         */
        isValidIP: function(ip) {
            const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            return ipRegex.test(ip);
        },
        
        /**
         * Validate URL
         */
        isValidURL: function(url) {
            try {
                new URL(url);
                return true;
            } catch (e) {
                return false;
            }
        },
        
        /**
         * Validate domain name
         */
        isValidDomain: function(domain) {
            const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
            return domainRegex.test(domain);
        },
        
        /**
         * Get severity color class
         */
        getSeverityColor: function(severity) {
            const colors = {
                'critical': 'danger',
                'high': 'warning',
                'medium': 'info',
                'low': 'success',
                'info': 'secondary'
            };
            return colors[severity] || 'secondary';
        },
        
        /**
         * Sanitize HTML content
         */
        sanitizeHTML: function(str) {
            const div = document.createElement('div');
            div.textContent = str;
            return div.innerHTML;
        },
        
        /**
         * Copy text to clipboard
         */
        copyToClipboard: function(text) {
            if (navigator.clipboard && window.isSecureContext) {
                return navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {
                    document.execCommand('copy');
                    return Promise.resolve();
                } catch (err) {
                    return Promise.reject(err);
                } finally {
                    textArea.remove();
                }
            }
        }
    };

    // ==========================================================================
    // API Client
    // ==========================================================================
    
    PentestApp.api = {
        
        /**
         * Make HTTP request
         */
        request: function(method, url, data = null, options = {}) {
            const defaultOptions = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            };
            
            if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                if (data instanceof FormData) {
                    delete defaultOptions.headers['Content-Type'];
                    defaultOptions.body = data;
                } else {
                    defaultOptions.body = JSON.stringify(data);
                }
            }
            
            const finalOptions = Object.assign(defaultOptions, options);
            
            return fetch(url, finalOptions)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json();
                    }
                    
                    return response.text();
                })
                .catch(error => {
                    console.error('API Request Error:', error);
                    throw error;
                });
        },
        
        /**
         * GET request
         */
        get: function(url, options = {}) {
            return this.request('GET', url, null, options);
        },
        
        /**
         * POST request
         */
        post: function(url, data, options = {}) {
            return this.request('POST', url, data, options);
        },
        
        /**
         * PUT request
         */
        put: function(url, data, options = {}) {
            return this.request('PUT', url, data, options);
        },
        
        /**
         * DELETE request
         */
        delete: function(url, options = {}) {
            return this.request('DELETE', url, null, options);
        },
        
        /**
         * Get system statistics
         */
        getSystemStats: function() {
            return this.get('/api/system/stats');
        },
        
        /**
         * Get active scans
         */
        getActiveScans: function() {
            return this.get('/api/scans/active');
        },
        
        /**
         * Start new scan
         */
        startScan: function(scanConfig) {
            return this.post('/scan/api/start', scanConfig);
        },
        
        /**
         * Stop scan
         */
        stopScan: function(scanId) {
            return this.post(`/scan/api/stop/${scanId}`);
        },
        
        /**
         * Get scan status
         */
        getScanStatus: function(scanId) {
            return this.get(`/scan/api/status/${scanId}`);
        }
    };

    // ==========================================================================
    // UI Components and Helpers
    // ==========================================================================
    
    PentestApp.ui = {
        
        /**
         * Show toast notification
         */
        showToast: function(message, type = 'info', duration = PentestApp.config.toastDuration) {
            const toastContainer = document.getElementById('toastContainer');
            if (!toastContainer) return;
            
            const toastId = PentestApp.utils.generateId('toast');
            const typeClass = type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary';
            const icon = type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle';
            
            const toastHTML = `
                <div class="toast align-items-center text-bg-${typeClass} border-0" role="alert" id="${toastId}">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${icon} me-2"></i>
                            ${PentestApp.utils.sanitizeHTML(message)}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                                data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHTML);
            
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, {
                autohide: true,
                delay: duration
            });
            
            toast.show();
            
            // Clean up after toast is hidden
            toastElement.addEventListener('hidden.bs.toast', function() {
                this.remove();
            });
            
            return toast;
        },
        
        /**
         * Show loading overlay
         */
        showLoading: function(message = 'Loading...') {
            const overlay = document.getElementById('loadingOverlay');
            const loadingText = overlay.querySelector('.loading-text');
            
            if (loadingText) {
                loadingText.textContent = message;
            }
            
            overlay.classList.add('show');
        },
        
        /**
         * Hide loading overlay
         */
        hideLoading: function() {
            const overlay = document.getElementById('loadingOverlay');
            overlay.classList.remove('show');
        },
        
        /**
         * Show confirmation modal
         */
        showConfirm: function(message, onConfirm, onCancel = null) {
            const modal = document.getElementById('confirmModal');
            if (!modal) return;
            
            const messageEl = document.getElementById('confirmMessage');
            const confirmBtn = document.getElementById('confirmAction');
            
            if (messageEl) {
                messageEl.textContent = message;
            }
            
            // Remove existing event listeners
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            
            // Add new event listener
            newConfirmBtn.addEventListener('click', function() {
                if (typeof onConfirm === 'function') {
                    onConfirm();
                }
                bootstrap.Modal.getInstance(modal).hide();
            });
            
            // Handle cancel
            modal.addEventListener('hidden.bs.modal', function() {
                if (typeof onCancel === 'function') {
                    onCancel();
                }
            }, { once: true });
            
            new bootstrap.Modal(modal).show();
        },
        
        /**
         * Update progress bar
         */
        updateProgress: function(progressBar, percentage, animated = true) {
            if (typeof progressBar === 'string') {
                progressBar = document.getElementById(progressBar);
            }
            
            if (!progressBar) return;
            
            percentage = Math.min(Math.max(percentage, 0), 100);
            
            if (animated) {
                progressBar.style.transition = 'width 0.3s ease';
            }
            
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            
            // Update text if progress text element exists
            const progressText = progressBar.parentElement.nextElementSibling;
            if (progressText && progressText.classList.contains('progress-text')) {
                progressText.textContent = Math.round(percentage) + '%';
            }
        },
        
        /**
         * Update counter with animation
         */
        updateCounter: function(element, targetValue, duration = 1000) {
            if (typeof element === 'string') {
                element = document.getElementById(element);
            }
            
            if (!element) return;
            
            const startValue = parseInt(element.textContent) || 0;
            const increment = (targetValue - startValue) / (duration / 16);
            let currentValue = startValue;
            
            const timer = setInterval(() => {
                currentValue += increment;
                
                if ((increment > 0 && currentValue >= targetValue) ||
                    (increment < 0 && currentValue <= targetValue)) {
                    currentValue = targetValue;
                    clearInterval(timer);
                }
                
                element.textContent = Math.round(currentValue);
                element.classList.add('animate');
                
                setTimeout(() => {
                    element.classList.remove('animate');
                }, 100);
            }, 16);
        },
        
        /**
         * Format table cell based on data type
         */
        formatTableCell: function(value, type = 'text') {
            switch (type) {
                case 'severity':
                    const colorClass = PentestApp.utils.getSeverityColor(value);
                    return `<span class="badge bg-${colorClass} severity-${value}">${value.toUpperCase()}</span>`;
                
                case 'status':
                    return `<span class="scan-status status-${value}">${value}</span>`;
                
                case 'date':
                    return PentestApp.utils.formatRelativeTime(value);
                
                case 'bytes':
                    return PentestApp.utils.formatBytes(value);
                
                case 'duration':
                    return PentestApp.utils.formatDuration(value);
                
                case 'url':
                    const shortUrl = value.length > 50 ? value.substring(0, 47) + '...' : value;
                    return `<a href="${value}" target="_blank" title="${value}">${shortUrl}</a>`;
                
                default:
                    return PentestApp.utils.sanitizeHTML(value);
            }
        },
        
        /**
         * Create pagination controls
         */
        createPagination: function(container, currentPage, totalPages, onPageChange) {
            if (typeof container === 'string') {
                container = document.getElementById(container);
            }
            
            if (!container || totalPages <= 1) return;
            
            let paginationHTML = '<nav><ul class="pagination justify-content-center">';
            
            // Previous button
            const prevDisabled = currentPage === 1 ? 'disabled' : '';
            paginationHTML += `<li class="page-item ${prevDisabled}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>`;
            
            // Page numbers
            for (let i = 1; i <= totalPages; i++) {
                const active = i === currentPage ? 'active' : '';
                paginationHTML += `<li class="page-item ${active}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>`;
            }
            
            // Next button
            const nextDisabled = currentPage === totalPages ? 'disabled' : '';
            paginationHTML += `<li class="page-item ${nextDisabled}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>`;
            
            paginationHTML += '</ul></nav>';
            
            container.innerHTML = paginationHTML;
            
            // Add event listeners
            container.addEventListener('click', function(e) {
                if (e.target.classList.contains('page-link')) {
                    e.preventDefault();
                    const page = parseInt(e.target.getAttribute('data-page'));
                    if (page && page >= 1 && page <= totalPages && page !== currentPage) {
                        onPageChange(page);
                    }
                }
            });
        }
    };

    // ==========================================================================
    // Event Handlers and Initialization
    // ==========================================================================
    
    /**
     * Initialize the application
     */
    function initializeApp() {
        // Set up global error handling
        window.addEventListener('error', function(e) {
            console.error('Global error:', e.error);
            PentestApp.ui.showToast('An unexpected error occurred', 'error');
        });
        
        // Set up unhandled promise rejection handling
        window.addEventListener('unhandledrejection', function(e) {
            console.error('Unhandled promise rejection:', e.reason);
            PentestApp.ui.showToast('An error occurred while processing your request', 'error');
        });
        
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Set up form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
        
        // Set up copy buttons
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
                const btn = e.target.classList.contains('copy-btn') ? e.target : e.target.closest('.copy-btn');
                const text = btn.getAttribute('data-copy') || btn.textContent;
                
                PentestApp.utils.copyToClipboard(text)
                    .then(() => {
                        PentestApp.ui.showToast('Copied to clipboard', 'success', 2000);
                    })
                    .catch(() => {
                        PentestApp.ui.showToast('Failed to copy to clipboard', 'error');
                    });
            }
        });
        
        // Set up keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], .search-input');
                if (searchInput) {
                    searchInput.focus();
                }
            }
        });
        
        console.log('PentestApp initialized successfully');
    }

    // ==========================================================================
    // Auto-initialization
    // ==========================================================================
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeApp);
    } else {
        initializeApp();
    }

    // Make global functions available
    window.showToast = PentestApp.ui.showToast;
    window.showConfirm = PentestApp.ui.showConfirm;
    window.showLoading = PentestApp.ui.showLoading;
    window.hideLoading = PentestApp.ui.hideLoading;

})();