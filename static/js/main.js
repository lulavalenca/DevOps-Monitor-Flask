// DevOps Monitor - Main JavaScript

// Configuração global
const config = {
    socket: null,
    charts: {},
    maxDataPoints: 20
};

// Inicializar quando documento carregar
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCharts();
    setupEventListeners();
});

// Inicializar Socket.IO
function initializeSocket() {
    config.socket = io();

    config.socket.on('connect', handleConnect);
    config.socket.on('disconnect', handleDisconnect);
    config.socket.on('system_metrics', handleSystemMetrics);
    config.socket.on('initial_data', handleInitialData);
    config.socket.on('error', handleError);

    console.log('🔌 Socket.IO inicializado');
}

// Handlers de conexão
function handleConnect() {
    console.log('✅ Conectado ao servidor');
    updateConnectionStatus(true);
}

function handleDisconnect() {
    console.log('❌ Desconectado do servidor');
    updateConnectionStatus(false);
}

function updateConnectionStatus(connected) {
    const statusBadge = document.getElementById('connection-status');
    if (connected) {
        statusBadge.innerHTML = '<i class="fas fa-wifi"></i> Conectado';
        statusBadge.className = 'badge status-connected';
    } else {
        statusBadge.innerHTML = '<i class="fas fa-wifi-slash"></i> Desconectado';
        statusBadge.className = 'badge status-disconnected';
    }
}

// Inicializar gráficos Chart.js
function initializeCharts() {
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    // CPU Chart
    config.charts.cpu = new Chart(
        document.getElementById('cpuChart'), {
            ...chartConfig,
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        }
    );

    // Memory Chart
    config.charts.memory = new Chart(
        document.getElementById('memoryChart'), {
            ...chartConfig,
            data: {
                labels: [],
                datasets: [{
                    label: 'Memory %',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        }
    );

    console.log('📊 Gráficos inicializados');
}

// Event Listeners
function setupEventListeners() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', requestManualUpdate);
    }
}

function requestManualUpdate() {
    const btn = document.getElementById('refreshBtn');
    btn.innerHTML = '<i class="fas fa-spinner spinner"></i> Atualizando...';
    btn.disabled = true;

    config.socket.emit('request_update');

    setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizar';
        btn.disabled = false;
    }, 1000);
}

// Handlers de dados
function handleInitialData(data) {
    console.log('📦 Dados iniciais recebidos');
    updateMetrics(data);
}

function handleSystemMetrics(data) {
    updateMetrics(data);
}

function handleError(data) {
    console.error('❌ Erro:', data.message);
    showNotification('Erro', data.message, 'danger');
}

// Atualizar métricas na interface
function updateMetrics(data) {
    const metrics = data.metrics;

    // Atualizar cards
    updateCard('cpu-value', metrics.cpu, '%');
    updateCard('memory-value', metrics.memory.percentage, '%');
    updateCard('disk-value', metrics.disk.percentage, '%');
    updateCard('network-value', (metrics.network.bytes_recv / 1024 / 1024).toFixed(1), ' MB');

    // Atualizar gráficos
    const time = new Date(metrics.timestamp).toLocaleTimeString();
    updateChart('cpu', time, metrics.cpu);
    updateChart('memory', time, metrics.memory.percentage);

    // Mostrar alertas
    if (data.alerts && data.alerts.length > 0) {
        showAlerts(data.alerts);
    }
}

function updateCard(elementId, value, unit) {
    const element = document.getElementById(elementId);
    if (element) {
        if (typeof value === 'number') {
            element.textContent = value.toFixed(1) + unit;
        } else {
            element.textContent = value + unit;
        }
    }
}

function updateChart(chartName, label, value) {
    const chart = config.charts[chartName];
    if (!chart) return;

    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    // Manter apenas os últimos N pontos
    if (chart.data.labels.length > config.maxDataPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update('none'); // Sem animação para melhor performance
}

function showAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    if (!container) return;

    container.innerHTML = '';

    alerts.forEach(alert => {
        const alertClass = alert.level === 'critical' ? 'danger' : 'warning';
        const alertHtml = `
            <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                <strong><i class="fas fa-exclamation-triangle"></i> ${alert.type}</strong>: ${alert.message}
                <small class="d-block mt-1">${new Date(alert.timestamp).toLocaleString()}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        container.innerHTML += alertHtml;
    });
}

function showNotification(title, message, type = 'info') {
    // Implementar toast notification se necessário
    console.log(`[${type}] ${title}: ${message}`);
}