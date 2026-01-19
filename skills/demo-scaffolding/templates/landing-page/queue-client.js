/**
 * {{PRODUCT}} Demo Queue Client
 *
 * Handles WebSocket communication with the queue manager
 * and manages UI state transitions.
 * Supports invite-based access control.
 */

class QueueClient {
    constructor() {
        this.ws = null;
        this.state = 'disconnected'; // disconnected, connected, queued, active, error
        this.sessionExpiresAt = null;
        this.timerInterval = null;
        this.inviteToken = this.getInviteToken();

        // UI Elements
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.startBtn = document.getElementById('start-demo-btn');
        this.queuePosition = document.getElementById('queue-position');
        this.positionNumber = document.getElementById('position-number');
        this.waitTime = document.getElementById('wait-time');
        this.leaveQueueBtn = document.getElementById('leave-queue-btn');
        this.terminalOverlay = document.getElementById('terminal-overlay');
        this.terminalIframe = document.getElementById('terminal-iframe');
        this.terminalTimer = document.getElementById('terminal-timer');
        this.terminalClose = document.getElementById('terminal-close');
        this.inviteError = document.getElementById('invite-error');
        this.errorTitle = document.getElementById('error-title');
        this.errorMessage = document.getElementById('error-message');
        this.heroSection = document.querySelector('.hero');

        // Check for invite token before proceeding
        if (!this.inviteToken) {
            this.showInviteRequired();
            return;
        }

        this.bindEvents();
        this.connect();
    }

    getInviteToken() {
        // Token is in the URL path: /TOKEN (4-64 chars, URL-safe)
        const path = window.location.pathname;
        const match = path.match(/^\/([A-Za-z0-9_-]{4,64})$/);
        return match ? match[1] : null;
    }

    showInviteRequired() {
        this.errorTitle.textContent = 'Invite Required';
        this.errorMessage.textContent = 'You need a valid invite link to access this demo. Please contact the administrator for an invite.';

        if (this.heroSection) {
            this.heroSection.hidden = true;
        }
        // Hide other sections too
        document.querySelectorAll('.scenarios, .commands, .features').forEach(el => {
            el.hidden = true;
        });
        if (this.inviteError) {
            this.inviteError.hidden = false;
        }
    }

    bindEvents() {
        this.startBtn.addEventListener('click', () => this.handleStartDemo());
        this.leaveQueueBtn.addEventListener('click', () => this.handleLeaveQueue());
        this.terminalClose.addEventListener('click', () => this.handleEndSession());
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to queue manager');
            this.state = 'connected';
            this.updateUI();
        };

        this.ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            } catch (err) {
                console.error('Failed to parse message:', err);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected from queue manager');
            this.state = 'disconnected';
            this.updateUI();

            // Attempt to reconnect after 3 seconds
            setTimeout(() => this.connect(), 3000);
        };

        this.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
        };

        // Heartbeat every 30 seconds
        setInterval(() => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }

    handleMessage(message) {
        console.log('Received:', message);

        switch (message.type) {
            case 'status':
                this.handleStatus(message);
                break;

            case 'queue_position':
                this.handleQueuePosition(message);
                break;

            case 'queue_full':
                this.handleQueueFull(message);
                break;

            case 'left_queue':
                this.handleLeftQueue();
                break;

            case 'session_starting':
                this.handleSessionStarting(message);
                break;

            case 'session_warning':
                this.handleSessionWarning(message);
                break;

            case 'session_ended':
                this.handleSessionEnded(message);
                break;

            case 'error':
                this.handleError(message);
                break;

            case 'invite_invalid':
                this.handleInviteInvalid(message);
                break;

            case 'session_token':
                // Set session cookie immediately on queue join (allows page refresh)
                if (message.session_token) {
                    document.cookie = `demo_session=${message.session_token}; path=/; SameSite=Lax`;
                }
                break;

            case 'heartbeat_ack':
                // Ignore heartbeat acknowledgments
                break;

            default:
                console.warn('Unknown message type:', message.type);
        }
    }

    handleStatus(message) {
        if (message.session_active) {
            this.setStatusBusy(message.queue_size);
        } else {
            this.setStatusAvailable();
        }
    }

    handleQueuePosition(message) {
        this.state = 'queued';
        this.positionNumber.textContent = message.position;
        this.waitTime.textContent = message.estimated_wait;
        this.updateUI();
    }

    handleQueueFull(message) {
        alert(message.message || 'Queue is full. Please try again later.');
        this.state = 'connected';
        this.updateUI();
    }

    handleLeftQueue() {
        this.state = 'connected';
        // Clear session cookie since we're leaving the queue
        document.cookie = 'demo_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        this.updateUI();
    }

    handleSessionStarting(message) {
        this.state = 'active';
        this.sessionExpiresAt = new Date(message.expires_at);

        // Set session cookie for Grafana access
        if (message.session_token) {
            document.cookie = `demo_session=${message.session_token}; path=/; SameSite=Lax`;
        }

        // Show terminal overlay
        this.terminalOverlay.hidden = false;
        this.terminalIframe.src = message.terminal_url || '/terminal';

        // Start countdown timer
        this.startTimer();
        this.updateUI();
    }

    handleSessionWarning(message) {
        // Visual warning - flash timer
        this.terminalTimer.style.color = '#f59e0b';
        this.terminalTimer.style.animation = 'pulse 1s infinite';
    }

    handleSessionEnded(message) {
        this.state = 'connected';
        this.sessionExpiresAt = null;

        // Clear session cookie
        document.cookie = 'demo_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';

        // Hide terminal overlay
        this.terminalOverlay.hidden = true;
        this.terminalIframe.src = '';

        // Stop timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }

        // Show reason
        if (message.reason === 'timeout') {
            alert('Your session has ended ({{SESSION_TIMEOUT}} minute limit). Thank you for trying {{PRODUCT}} Assistant Skills!');
        } else if (message.reason === 'disconnected') {
            alert('Session ended due to disconnection.');
        }

        this.updateUI();
    }

    handleError(message) {
        console.error('Server error:', message.message);
        alert(`Error: ${message.message}`);
    }

    handleInviteInvalid(message) {
        console.error('Invite invalid:', message.reason, message.message);
        this.state = 'error';

        // Error titles based on reason
        const titles = {
            'not_found': 'Invite Not Found',
            'expired': 'Invite Expired',
            'used': 'Invite Already Used',
            'revoked': 'Invite Revoked',
            'invalid': 'Invalid Invite'
        };

        this.errorTitle.textContent = titles[message.reason] || 'Invalid Invite';
        this.errorMessage.textContent = message.message || 'This invite link is not valid.';

        // Hide all content and show error
        if (this.heroSection) {
            this.heroSection.hidden = true;
        }
        document.querySelectorAll('.scenarios, .commands, .features').forEach(el => {
            el.hidden = true;
        });
        if (this.inviteError) {
            this.inviteError.hidden = false;
        }

        this.startBtn.classList.remove('loading');
    }

    handleStartDemo() {
        if (this.ws.readyState !== WebSocket.OPEN) {
            alert('Not connected. Please wait...');
            return;
        }

        const message = { type: 'join_queue' };
        if (this.inviteToken) {
            message.inviteToken = this.inviteToken;
        }

        this.ws.send(JSON.stringify(message));
        this.startBtn.classList.add('loading');
    }

    handleLeaveQueue() {
        if (this.ws.readyState !== WebSocket.OPEN) return;

        this.ws.send(JSON.stringify({ type: 'leave_queue' }));
    }

    handleEndSession() {
        if (confirm('Are you sure you want to end your demo session?')) {
            // The session will end when the connection closes
            this.terminalIframe.src = '';
            this.handleSessionEnded({ reason: 'user_ended' });
        }
    }

    setStatusAvailable() {
        this.statusIndicator.className = 'status-indicator available';
        this.statusText.textContent = 'Session available';
        this.startBtn.disabled = false;
    }

    setStatusBusy(queueSize) {
        this.statusIndicator.className = 'status-indicator busy';
        if (queueSize > 0) {
            this.statusText.textContent = `${queueSize} in queue`;
        } else {
            this.statusText.textContent = 'Session in progress';
        }
        this.startBtn.disabled = false;
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            if (!this.sessionExpiresAt) return;

            const now = new Date();
            const remaining = this.sessionExpiresAt - now;

            if (remaining <= 0) {
                this.terminalTimer.textContent = '00:00';
                clearInterval(this.timerInterval);
                return;
            }

            const minutes = Math.floor(remaining / 60000);
            const seconds = Math.floor((remaining % 60000) / 1000);
            this.terminalTimer.textContent =
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    updateUI() {
        switch (this.state) {
            case 'disconnected':
                this.statusIndicator.className = 'status-indicator';
                this.statusText.textContent = 'Connecting...';
                this.startBtn.disabled = true;
                this.startBtn.classList.remove('loading');
                this.queuePosition.hidden = true;
                break;

            case 'connected':
                this.startBtn.classList.remove('loading');
                this.queuePosition.hidden = true;
                break;

            case 'queued':
                this.statusIndicator.className = 'status-indicator queued';
                this.statusText.textContent = 'In queue';
                this.startBtn.classList.remove('loading');
                this.startBtn.disabled = true;
                this.queuePosition.hidden = false;
                break;

            case 'active':
                this.startBtn.classList.remove('loading');
                this.queuePosition.hidden = true;
                break;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.queueClient = new QueueClient();
});
