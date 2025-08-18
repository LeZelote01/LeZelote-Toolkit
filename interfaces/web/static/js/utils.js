/*
 * Utility Functions for Pentest-USB Toolkit
 * =========================================
 */

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        console.error('Toast container not found');
        return;
    }
    
    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    const typeConfig = {
        success: {
            class: 'text-bg-success',
            icon: 'fa-check-circle'
        },
        error: {
            class: 'text-bg-danger',
            icon: 'fa-exclamation-triangle'
        },
        warning: {
            class: 'text-bg-warning',
            icon: 'fa-exclamation-circle'
        },
        info: {
            class: 'text-bg-info',
            icon: 'fa-info-circle'
        }
    };
    
    const config = typeConfig[type] || typeConfig.info;
    
    const toastHtml = `
        <div class="toast align-items-center ${config.class} border-0" 
             role="alert" 
             id="${toastId}" 
             data-bs-autohide="true" 
             data-bs-delay="${duration}">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center">
                    <i class="fas ${config.icon} me-2"></i>
                    <span>${escapeHtml(message)}</span>
                </div>
                <button type="button" 
                        class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" 
                        aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    
    // Show toast
    toast.show();
    
    // Browser notification for important messages
    if ((type === 'error' || type === 'warning') && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('Pentest-USB Toolkit', {
            body: message,
            icon: '/static/img/logo.png',
            tag: 'pentest-notification'
        });
    }
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
    
    return toast;
}

/**
 * Show loading overlay
 */
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        const loadingText = overlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
        overlay.style.display = 'flex';
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * Show progress dialog
 */
function showProgress(title = 'Processing', initialMessage = 'Starting...') {
    const progressId = 'progressModal-' + Date.now();
    
    const modalHtml = `
        <div class="modal fade" id="${progressId}" tabindex="-1" data-bs-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-cog fa-spin me-2"></i>${escapeHtml(title)}
                        </h5>
                    </div>
                    <div class="modal-body">
                        <div class="progress mb-3">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 role="progressbar" 
                                 style="width: 0%" 
                                 id="${progressId}-bar"></div>
                        </div>
                        <div class="progress-message" id="${progressId}-message">
                            ${escapeHtml(initialMessage)}
                        </div>
                        <div class="progress-logs mt-3" id="${progressId}-logs" style="max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.875rem; background: #f8f9fa; padding: 0.75rem; border-radius: 0.375rem; display: none;">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="${progressId}-close" style="display: none;">Close</button>
                        <button type="button" class="btn btn-danger" id="${progressId}-cancel">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById(progressId), {
        backdrop: 'static',
        keyboard: false
    });
    
    modal.show();
    
    return {
        id: progressId,
        modal: modal,
        updateProgress: function(percentage, message) {
            const bar = document.getElementById(`${progressId}-bar`);
            const messageEl = document.getElementById(`${progressId}-message`);
            
            if (bar) {
                bar.style.width = `${percentage}%`;
                bar.setAttribute('aria-valuenow', percentage);
            }
            
            if (messageEl && message) {
                messageEl.textContent = message;
            }
        },
        addLog: function(message, type = 'info') {
            const logsEl = document.getElementById(`${progressId}-logs`);
            if (logsEl) {
                logsEl.style.display = 'block';
                const timestamp = new Date().toLocaleTimeString();
                const logClass = type === 'error' ? 'text-danger' : type === 'warning' ? 'text-warning' : 'text-muted';
                logsEl.innerHTML += `<div class="${logClass}">[${timestamp}] ${escapeHtml(message)}</div>`;
                logsEl.scrollTop = logsEl.scrollHeight;
            }
        },
        complete: function(success = true, finalMessage = 'Completed') {
            const bar = document.getElementById(`${progressId}-bar`);
            const messageEl = document.getElementById(`${progressId}-message`);
            const closeBtn = document.getElementById(`${progressId}-close`);
            const cancelBtn = document.getElementById(`${progressId}-cancel`);
            
            if (bar) {
                bar.style.width = '100%';
                bar.classList.remove('progress-bar-animated');
                bar.classList.add(success ? 'bg-success' : 'bg-danger');
            }
            
            if (messageEl) {
                messageEl.textContent = finalMessage;
            }
            
            if (closeBtn && cancelBtn) {
                closeBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'none';
            }
        },
        close: function() {
            modal.hide();
            setTimeout(() => {
                document.getElementById(progressId).remove();
            }, 300);
        }
    };
}

/**
 * Make AJAX request with proper error handling
 */
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    // Add CSRF token if available
    if (window.PentestApp && window.PentestApp.csrfToken) {
        defaultOptions.headers['X-CSRFToken'] = window.PentestApp.csrfToken;
    }
    
    const finalOptions = { ...defaultOptions, ...options };
    
    // Merge headers properly
    if (options.headers) {
        finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
    }
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return response.text();
            }
        })
        .catch(error => {
            console.error('Request failed:', error);
            throw error;
        });
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

/**
 * Throttle function to limit function calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format time duration
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
    }
}

/**
 * Format bytes to human readable format
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Get relative time string
 */
function getRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) return 'just now';
    if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
    if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
    if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text, successMessage = 'Copied to clipboard') {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text).then(() => {
            showToast(successMessage, 'success', 2000);
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            fallbackCopyTextToClipboard(text, successMessage);
        });
    } else {
        fallbackCopyTextToClipboard(text, successMessage);
    }
}

/**
 * Fallback copy to clipboard for older browsers
 */
function fallbackCopyTextToClipboard(text, successMessage) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast(successMessage, 'success', 2000);
        } else {
            showToast('Failed to copy to clipboard', 'error');
        }
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showToast('Copy to clipboard not supported', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Generate random ID
 */
function generateId(prefix = 'id') {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate IP address format
 */
function isValidIP(ip) {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}

/**
 * Validate URL format
 */
function isValidURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Download file from blob
 */
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

/**
 * Download file from URL
 */
function downloadFile(url, filename) {
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename || '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

/**
 * Parse CSV data
 */
function parseCSV(csvText, delimiter = ',') {
    const lines = csvText.split('\n');
    const result = [];
    const headers = lines[0].split(delimiter).map(header => header.trim().replace(/"/g, ''));
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
            const values = line.split(delimiter).map(value => value.trim().replace(/"/g, ''));
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = values[index] || '';
            });
            result.push(obj);
        }
    }
    
    return result;
}

/**
 * Convert object to CSV
 */
function objectToCSV(data, delimiter = ',') {
    if (!Array.isArray(data) || data.length === 0) {
        return '';
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(delimiter),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header] || '';
                return typeof value === 'string' && value.includes(delimiter) ? `"${value}"` : value;
            }).join(delimiter)
        )
    ].join('\n');
    
    return csvContent;
}

/**
 * Local storage helpers with error handling
 */
const storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('LocalStorage set error:', error);
            return false;
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('LocalStorage get error:', error);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('LocalStorage remove error:', error);
            return false;
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('LocalStorage clear error:', error);
            return false;
        }
    }
};

// Expose utility functions globally
window.utils = {
    showToast,
    showLoading,
    hideLoading,
    showProgress,
    makeRequest,
    debounce,
    throttle,
    formatDuration,
    formatBytes,
    getRelativeTime,
    copyToClipboard,
    generateId,
    isValidEmail,
    isValidIP,
    isValidURL,
    downloadBlob,
    downloadFile,
    parseCSV,
    objectToCSV,
    storage
};

// Also expose individual functions for backward compatibility
Object.assign(window, window.utils);