// Variáveis globais
let isAdminLoggedIn = false;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    checkAdminStatus();
    loadHolidays();
    
    // Define datas padrão
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('baseDate').value = today;
    document.getElementById('startDate').value = today;
});

// Funções de utilidade
function showToast(message, type = 'info') {
    const toastBody = document.getElementById('toastBody');
    const toast = document.getElementById('toast');
    
    toastBody.textContent = message;
    
    // Remove classes anteriores e adiciona a nova
    toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : 'bg-success text-white'}`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Funções de administração
function toggleAdminPanel() {
    const panel = document.getElementById('adminPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

async function checkAdminStatus() {
    try {
        const response = await fetch('/api/admin/check');
        const data = await response.json();
        
        if (data.is_admin) {
            isAdminLoggedIn = true;
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('adminControls').style.display = 'block';
        } else {
            isAdminLoggedIn = false;
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('adminControls').style.display = 'none';
        }
    } catch (error) {
        console.error('Erro ao verificar status do admin:', error);
    }
}

async function adminLogin() {
    const username = document.getElementById('adminUsername').value;
    const password = document.getElementById('adminPassword').value;
    
    if (!username || !password) {
        showToast('Por favor, preencha usuário e senha', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Login realizado com sucesso!');
            checkAdminStatus();
            document.getElementById('adminUsername').value = '';
            document.getElementById('adminPassword').value = '';
        } else {
            showToast(data.error || 'Erro no login', 'error');
        }
    } catch (error) {
        showToast('Erro ao fazer login', 'error');
    }
}

async function adminLogout() {
    try {
        await fetch('/api/admin/logout', { method: 'POST' });
        showToast('Logout realizado com sucesso!');
        checkAdminStatus();
    } catch (error) {
        showToast('Erro ao fazer logout', 'error');
    }
}

// Funções de feriados
function showHolidayForm() {
    document.getElementById('holidayForm').style.display = 'block';
}

function hideHolidayForm() {
    document.getElementById('holidayForm').style.display = 'none';
    // Limpa o formulário
    document.getElementById('holidayName').value = '';
    document.getElementById('holidayDate').value = '';
    document.getElementById('holidayType').value = 'nacional';
    document.getElementById('holidayState').value = '';
    document.getElementById('holidayCity').value = '';
}

async function saveHoliday() {
    const name = document.getElementById('holidayName').value;
    const date = document.getElementById('holidayDate').value;
    const type = document.getElementById('holidayType').value;
    const state = document.getElementById('holidayState').value;
    const city = document.getElementById('holidayCity').value;
    
    if (!name || !date) {
        showToast('Nome e data são obrigatórios', 'error');
        return;
    }
    
    const holidayData = { name, date, type };
    if (state) holidayData.state = state.toUpperCase();
    if (city) holidayData.city = city;
    
    try {
        const response = await fetch('/api/holidays', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(holidayData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Feriado cadastrado com sucesso!');
            hideHolidayForm();
            loadHolidays();
        } else {
            showToast(data.error || 'Erro ao cadastrar feriado', 'error');
        }
    } catch (error) {
        showToast('Erro ao cadastrar feriado', 'error');
    }
}

async function importNationalHolidays() {
    const year = new Date().getFullYear();
    
    try {
        const response = await fetch(`/api/holidays/import-national/${year}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message);
            loadHolidays();
        } else {
            showToast(data.error || 'Erro ao importar feriados', 'error');
        }
    } catch (error) {
        showToast('Erro ao importar feriados', 'error');
    }
}

async function loadHolidays() {
    const startDate = document.getElementById('filterStartDate').value;
    const endDate = document.getElementById('filterEndDate').value;
    const state = document.getElementById('filterState').value;
    const city = document.getElementById('filterCity').value;
    
    let url = '/api/holidays?';
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (state) params.append('state', state.toUpperCase());
    if (city) params.append('city', city);
    
    url += params.toString();
    
    try {
        const response = await fetch(url);
        const holidays = await response.json();
        
        displayHolidays(holidays);
    } catch (error) {
        showToast('Erro ao carregar feriados', 'error');
    }
}

function displayHolidays(holidays) {
    const container = document.getElementById('holidaysList');
    
    if (holidays.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Nenhum feriado encontrado no período selecionado.</p>';
        return;
    }
    
    const holidaysHtml = holidays.map(holiday => `
        <div class="holiday-item">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <div class="holiday-date">${formatDate(holiday.date)}</div>
                    <div class="fw-bold">${holiday.name}</div>
                    ${holiday.state ? `<small class="text-muted">Estado: ${holiday.state}</small><br>` : ''}
                    ${holiday.city ? `<small class="text-muted">Cidade: ${holiday.city}</small>` : ''}
                </div>
                <span class="holiday-type ${holiday.type}">${holiday.type}</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = holidaysHtml;
}

// Funções de cálculo de dias úteis
async function countBusinessDays() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const state = document.getElementById('countState').value;
    const city = document.getElementById('countCity').value;
    
    if (!startDate || !endDate) {
        showToast('Por favor, preencha as datas inicial e final', 'error');
        return;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
        showToast('A data inicial deve ser anterior à data final', 'error');
        return;
    }
    
    const requestData = { start_date: startDate, end_date: endDate };
    if (state) requestData.state = state.toUpperCase();
    if (city) requestData.city = city;
    
    try {
        const response = await fetch('/api/business-days/count', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayCountResult(data);
        } else {
            showToast(data.error || 'Erro ao calcular dias úteis', 'error');
        }
    } catch (error) {
        showToast('Erro ao calcular dias úteis', 'error');
    }
}

function displayCountResult(data) {
    const container = document.getElementById('countResult');
    
    container.innerHTML = `
        <div class="result-card">
            <div class="result-number">${data.business_days}</div>
            <div class="result-text">
                dias úteis entre ${formatDate(data.start_date)} e ${formatDate(data.end_date)}
                ${data.state ? `<br>Estado: ${data.state}` : ''}
                ${data.city ? `<br>Cidade: ${data.city}` : ''}
            </div>
        </div>
    `;
}

async function addBusinessDays() {
    const baseDate = document.getElementById('baseDate').value;
    const daysToAdd = parseInt(document.getElementById('daysToAdd').value);
    const state = document.getElementById('addState').value;
    const city = document.getElementById('addCity').value;
    
    if (!baseDate || isNaN(daysToAdd)) {
        showToast('Por favor, preencha a data base e o número de dias', 'error');
        return;
    }
    
    const requestData = { 
        start_date: baseDate, 
        [daysToAdd >= 0 ? 'days_to_add' : 'days_to_subtract']: Math.abs(daysToAdd)
    };
    if (state) requestData.state = state.toUpperCase();
    if (city) requestData.city = city;
    
    const endpoint = daysToAdd >= 0 ? '/api/business-days/add' : '/api/business-days/subtract';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayAddResult(data, daysToAdd >= 0);
        } else {
            showToast(data.error || 'Erro ao calcular data', 'error');
        }
    } catch (error) {
        showToast('Erro ao calcular data', 'error');
    }
}

function displayAddResult(data, isAddition) {
    const container = document.getElementById('addResult');
    const operation = isAddition ? 'adicionando' : 'subtraindo';
    const days = data.days_added || data.days_subtracted;
    
    container.innerHTML = `
        <div class="result-card">
            <div class="result-number">${formatDate(data.result_date)}</div>
            <div class="result-text">
                ${operation} ${days} dias úteis de ${formatDate(data.start_date)}
                ${data.state ? `<br>Estado: ${data.state}` : ''}
                ${data.city ? `<br>Cidade: ${data.city}` : ''}
            </div>
        </div>
    `;
}