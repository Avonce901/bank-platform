/**
 * Frontend JavaScript Application
 * Real-time WebSocket updates, API interactions, UI management
 */

// Get API token from localStorage
const getToken = () => localStorage.getItem('authToken');

// WebSocket connection
let socket = null;
let dashboardSocket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setupEventListeners();
    connectWebSockets();
});

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('transferForm')?.addEventListener('submit', handleTransfer);
    document.getElementById('depositForm')?.addEventListener('submit', handleDeposit);
    document.getElementById('cardForm')?.addEventListener('submit', handleCreateCard);
}

// WebSocket Connection
function connectWebSockets() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const dashboardUrl = `${protocol}//${window.location.host}/ws/dashboard/`;
    
    dashboardSocket = new WebSocket(dashboardUrl);
    
    dashboardSocket.onopen = () => {
        console.log('Dashboard WebSocket connected');
        updateConnectionStatus(true);
        reconnectAttempts = 0;
    };
    
    dashboardSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    dashboardSocket.onclose = () => {
        console.log('Dashboard WebSocket disconnected');
        updateConnectionStatus(false);
        attemptReconnect();
    };
    
    dashboardSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };
}

function attemptReconnect() {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        setTimeout(connectWebSockets, 3000 * reconnectAttempts);
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'dashboard_update':
            updateDashboard(data.data);
            break;
        case 'balance_update':
            updateBalance(data.balance);
            break;
        case 'transaction':
            addTransactionToList(data.transaction);
            break;
        case 'notification':
            showNotification(data.message, 'info');
            break;
        case 'alert':
            showNotification(data.message, 'warning');
            break;
    }
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (connected) {
        status.textContent = 'Connected';
        status.className = 'status-indicator connected';
    } else {
        status.textContent = 'Disconnected';
        status.className = 'status-indicator disconnected';
    }
}

// Load Dashboard Data
function loadDashboardData() {
    const token = getToken();
    
    fetch('/api/accounts/me/', {
        headers: { 'Authorization': `Token ${token}` }
    })
    .then(response => response.json())
    .then(accounts => {
        displayAccounts(accounts);
        updateSummary(accounts);
    })
    .catch(error => console.error('Error loading accounts:', error));
}

function updateSummary(accounts) {
    let totalBalance = 0;
    let cardCount = 0;
    
    accounts.forEach(account => {
        totalBalance += parseFloat(account.balance);
        cardCount += account.virtual_cards?.length || 0;
    });
    
    document.getElementById('totalBalance').textContent = `$${totalBalance.toFixed(2)}`;
    document.getElementById('accountCount').textContent = accounts.length;
    document.getElementById('cardCount').textContent = cardCount;
}

function updateDashboard(data) {
    if (data.total_balance) {
        document.getElementById('totalBalance').textContent = `$${data.total_balance}`;
    }
    if (data.accounts_count) {
        document.getElementById('accountCount').textContent = data.accounts_count;
    }
    if (data.pending_transfers !== undefined) {
        document.getElementById('pendingTransfers').textContent = data.pending_transfers;
    }
}

// Display Accounts
function displayAccounts(accounts) {
    const container = document.getElementById('accountsList');
    container.innerHTML = '';
    
    accounts.forEach(account => {
        const item = document.createElement('div');
        item.className = 'account-item';
        item.innerHTML = `
            <div>
                <h4>${account.name}</h4>
                <p>Account: ${account.account_number}</p>
                <p>Type: ${account.account_type}</p>
            </div>
            <div class="amount-badge">$${parseFloat(account.balance).toFixed(2)}</div>
        `;
        container.appendChild(item);
    });
}

// Handle Transfer
async function handleTransfer(e) {
    e.preventDefault();
    
    const amount = document.getElementById('amount').value;
    const receiverAccount = document.getElementById('receiverAccount').value;
    const description = document.getElementById('transferDescription').value;
    const token = getToken();
    
    try {
        // Get sender account
        const accountResponse = await fetch('/api/accounts/me/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        const accounts = await accountResponse.json();
        const senderAccount = accounts[0];
        
        const response = await fetch(`/api/accounts/${senderAccount.id}/transfer/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                receiver_account_number: receiverAccount,
                amount: amount,
                description: description
            })
        });
        
        if (response.ok) {
            const transfer = await response.json();
            showNotification(`Transfer of $${amount} sent successfully!`, 'success');
            document.getElementById('transferForm').reset();
            loadDashboardData();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Transfer failed', 'error');
        }
    } catch (error) {
        console.error('Transfer error:', error);
        showNotification('Transfer failed', 'error');
    }
}

// Handle Deposit
async function handleDeposit(e) {
    e.preventDefault();
    
    const amount = document.getElementById('depositAmount').value;
    const method = document.getElementById('depositMethod').value;
    const description = document.getElementById('depositDescription').value;
    const token = getToken();
    
    try {
        // Get account
        const accountResponse = await fetch('/api/accounts/me/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        const accounts = await accountResponse.json();
        const account = accounts[0];
        
        let url = `/api/accounts/${account.id}/deposit/`;
        
        if (method === 'stripe') {
            // Handle Stripe payment
            url = `/api/accounts/${account.id}/stripe_deposit/`;
            // TODO: Integrate Stripe.js for payment processing
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                amount: amount,
                deposit_method: method,
                description: description
            })
        });
        
        if (response.ok) {
            showNotification(`Deposit of $${amount} successful!`, 'success');
            document.getElementById('depositForm').reset();
            loadDashboardData();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Deposit failed', 'error');
        }
    } catch (error) {
        console.error('Deposit error:', error);
        showNotification('Deposit failed', 'error');
    }
}

// Virtual Card Management
function showCreateCardForm() {
    document.getElementById('createCardForm').classList.remove('hidden');
}

function closeCreateCardForm() {
    document.getElementById('createCardForm').classList.add('hidden');
}

async function handleCreateCard(e) {
    e.preventDefault();
    
    const cardholderName = document.getElementById('cardholderName').value;
    const dailyLimit = document.getElementById('dailyLimit').value;
    const monthlyLimit = document.getElementById('monthlyLimit').value;
    const token = getToken();
    
    try {
        const response = await fetch('/api/cards/create_card/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                cardholder_name: cardholderName,
                daily_limit: dailyLimit,
                monthly_limit: monthlyLimit
            })
        });
        
        if (response.ok) {
            const card = await response.json();
            showNotification('Virtual card created successfully!', 'success');
            document.getElementById('cardForm').reset();
            closeCreateCardForm();
            loadVirtualCards();
        } else {
            const error = await response.json();
            showNotification(error.error || 'Card creation failed', 'error');
        }
    } catch (error) {
        console.error('Card creation error:', error);
        showNotification('Card creation failed', 'error');
    }
}

async function loadVirtualCards() {
    const token = getToken();
    
    try {
        const response = await fetch('/api/cards/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        const cards = await response.json();
        displayVirtualCards(cards);
    } catch (error) {
        console.error('Error loading cards:', error);
    }
}

function displayVirtualCards(cards) {
    const container = document.getElementById('cardsContainer');
    container.innerHTML = '';
    
    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = 'virtual-card';
        cardElement.innerHTML = `
            <div class="card-header">
                <div class="card-chip"></div>
                <span class="card-status">${card.status}</span>
            </div>
            <div class="card-number">${card.card_number ? card.card_number.substring(0, 4) + ' **** **** ' + card.card_number.substring(12) : '****'}</div>
            <div class="card-footer">
                <div>
                    <div class="card-expiry">Valid Thru: ${card.expiry_date}</div>
                    <div class="card-holder">${card.cardholder_name}</div>
                </div>
            </div>
            <div class="card-actions">
                <button onclick="lockCard(${card.id})" class="btn btn-small">Lock</button>
                <button onclick="cancelCard(${card.id})" class="btn btn-small">Cancel</button>
            </div>
        `;
        container.appendChild(cardElement);
    });
}

async function lockCard(cardId) {
    const token = getToken();
    
    try {
        const response = await fetch(`/api/cards/${cardId}/lock_card/`, {
            method: 'POST',
            headers: { 'Authorization': `Token ${token}` }
        });
        
        if (response.ok) {
            showNotification('Card locked successfully', 'success');
            loadVirtualCards();
        }
    } catch (error) {
        console.error('Error locking card:', error);
    }
}

async function cancelCard(cardId) {
    const token = getToken();
    
    if (confirm('Are you sure you want to cancel this card?')) {
        try {
            const response = await fetch(`/api/cards/${cardId}/cancel_card/`, {
                method: 'POST',
                headers: { 'Authorization': `Token ${token}` }
            });
            
            if (response.ok) {
                showNotification('Card cancelled', 'success');
                loadVirtualCards();
            }
        } catch (error) {
            console.error('Error cancelling card:', error);
        }
    }
}

// Tab Navigation
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'cards') {
        loadVirtualCards();
    } else if (tabName === 'transactions') {
        loadTransactions();
    } else if (tabName === 'transfers') {
        loadTransfers();
    }
}

async function loadTransactions() {
    const token = getToken();
    
    try {
        const response = await fetch('/api/transactions/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function displayTransactions(transactions) {
    const container = document.getElementById('transactionsList');
    container.innerHTML = '';
    
    transactions.forEach(tx => {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        
        const badgeClass = tx.status === 'completed' ? 'badge-success' : 
                          tx.status === 'pending' ? 'badge-warning' : 'badge-danger';
        
        item.innerHTML = `
            <div>
                <h4>${tx.transaction_type.toUpperCase()}</h4>
                <p>${tx.description}</p>
                <small>${new Date(tx.created_at).toLocaleDateString()}</small>
            </div>
            <div>
                <span class="amount-badge">${tx.amount > 0 ? '+' : ''}$${parseFloat(tx.amount).toFixed(2)}</span>
                <span class="badge ${badgeClass}">${tx.status}</span>
            </div>
        `;
        container.appendChild(item);
    });
}

async function loadTransfers() {
    const token = getToken();
    
    try {
        const response = await fetch('/api/transfers/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        const transfers = await response.json();
        displayTransfers(transfers);
    } catch (error) {
        console.error('Error loading transfers:', error);
    }
}

function displayTransfers(transfers) {
    const container = document.getElementById('transfersList');
    container.innerHTML = '';
    
    transfers.forEach(transfer => {
        const item = document.createElement('div');
        item.className = 'transfer-item';
        
        const badgeClass = transfer.status === 'completed' ? 'badge-success' :
                          transfer.status === 'pending' ? 'badge-warning' : 'badge-danger';
        
        item.innerHTML = `
            <div>
                <h4>${transfer.sender_name} → ${transfer.receiver_name}</h4>
                <p>Reference: ${transfer.reference_id}</p>
                <small>${new Date(transfer.created_at).toLocaleDateString()}</small>
            </div>
            <div>
                <span class="amount-badge">$${parseFloat(transfer.amount).toFixed(2)}</span>
                <span class="badge ${badgeClass}">${transfer.status}</span>
            </div>
        `;
        container.appendChild(item);
    });
}

function addTransactionToList(transaction) {
    const container = document.getElementById('transactionsList');
    if (container) {
        const item = document.createElement('div');
        item.className = 'transaction-item';
        item.innerHTML = `
            <div>
                <h4>${transaction.transaction_type}</h4>
                <p>${transaction.description}</p>
            </div>
            <div>
                <span class="amount-badge">$${transaction.amount}</span>
            </div>
        `;
        container.insertBefore(item, container.firstChild);
    }
}

function updateBalance(balance) {
    document.getElementById('totalBalance').textContent = `$${balance}`;
}

// Notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${
            type === 'success' ? '#28a745' :
            type === 'error' ? '#dc3545' :
            type === 'warning' ? '#ffc107' : '#17a2b8'
        };
        color: ${type === 'warning' ? '#000' : '#fff'};
        padding: 1rem 1.5rem;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-in;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Logout
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = '/login/';
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
