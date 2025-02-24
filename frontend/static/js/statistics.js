// Глобальные переменные для графиков
let registrationsChart = null;
let transportChart = null;

// Глобальные переменные
let currentFilter = 'personal';
let currentEmployeeId = null;

// Константы для статусов
const ONBOARDING_STATUSES = {
    WILL_BE_VERIFIED: 'Оформится',
    VERIFIED: 'Оформлен',
    REJECTED_BY_HUB: 'Отказ хаба',
    REJECTED_BY_COURIER: 'Отказ курьера'
};

// Загрузка статистики
async function loadStatistics() {
    try {
        showLoading();
        
        // Получаем выбранные значения фильтров
        const region = document.getElementById('regionFilter').value;
        const dateFrom = document.getElementById('dateFrom').value;
        const dateTo = document.getElementById('dateTo').value;
        const employee = document.getElementById('employeeFilter').value;

        const response = await fetch(`/api/onboarding/statistics?` + new URLSearchParams({
            region: region,
            date_from: dateFrom,
            date_to: dateTo,
            employee: employee
        }), {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Ошибка при загрузке статистики');
        }

        const data = await response.json();
        
        // Обновляем показатели
        updateMetrics(data.metrics);
        
        // Обновляем график
        updateChart(data.chart_data);
        
        // Обновляем таблицу сотрудников
        if (employee === 'all') {
            updateEmployeesTable(data.employees);
        }

    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при загрузке статистики');
    } finally {
        hideLoading();
    }
}

function updateMetrics(metrics) {
    document.getElementById('totalCouriers').textContent = metrics.total;
    document.getElementById('verifiedCouriers').textContent = metrics.verified;
    document.getElementById('willBeVerifiedCouriers').textContent = metrics.will_be_verified;
    document.getElementById('rejectedByHubCouriers').textContent = metrics.rejected_by_hub;
    document.getElementById('rejectedByCourierCouriers').textContent = metrics.rejected_by_courier;
}

function updateEmployeesTable(employees) {
    const tbody = document.getElementById('employeesTableBody');
    tbody.innerHTML = '';

    employees.forEach(emp => {
        tbody.innerHTML += `
            <tr>
                <td>${emp.name}</td>
                <td>${emp.total}</td>
                <td>${emp.verified}</td>
                <td>${emp.will_be_verified}</td>
                <td>${emp.rejected_by_hub}</td>
                <td>${emp.rejected_by_courier}</td>
            </tr>
        `;
    });
}

// Загрузка списка сотрудников
async function loadEmployees() {
    try {
        console.log('Загрузка списка сотрудников...');
        const response = await fetch('/api/onboarding/employees', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });

        console.log('Статус ответа:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка от сервера:', errorData);
            throw new Error(errorData.detail || 'Ошибка при загрузке списка сотрудников');
        }

        const employees = await response.json();
        console.log('Получены сотрудники:', employees);
        
        const select = document.getElementById('employeeSelect');
        select.innerHTML = '<option value="">Выберите сотрудника</option>';
        
        employees.forEach(emp => {
            select.innerHTML += `<option value="${emp.id}">${emp.username}</option>`;
        });
    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при загрузке списка сотрудников');
    }
}

// Обновление статистики
function updateStats(data) {
    document.getElementById('totalCouriers').textContent = data.total_couriers;
    document.getElementById('activeCouriers').textContent = data.active_couriers;
    document.getElementById('inactiveCouriers').textContent = data.inactive_couriers;
    document.getElementById('blockedCouriers').textContent = data.blocked_couriers;
}

// Обновление графика регистраций
function updateRegistrationsChart(data) {
    const ctx = document.getElementById('registrationsChart').getContext('2d');
    
    if (registrationsChart) {
        registrationsChart.destroy();
    }

    registrationsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Количество регистраций',
                data: data.map(item => item.count),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Обновление графика транспорта
function updateTransportChart(data) {
    const ctx = document.getElementById('transportChart').getContext('2d');
    
    if (transportChart) {
        transportChart.destroy();
    }

    transportChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Обновление таблицы статистики
function updateStatsTable(data) {
    const tbody = document.getElementById('statsTableBody');
    tbody.innerHTML = '';

    data.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td>${row.date}</td>
                <td>${row.new_registrations}</td>
                <td>${row.active_couriers}</td>
                <td>${row.churn_rate}%</td>
                <td>${row.conversion_rate}%</td>
            </tr>
        `;
    });
}

// Показ ошибки
function showError(message) {
    console.error(message);
    // Добавим визуальное отображение ошибки
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);
    
    // Удалим сообщение через 5 секунд
    setTimeout(() => errorDiv.remove(), 5000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что мы на странице статистики
    if (document.getElementById('statisticsContainer')) {
        loadEmployees();
        
        // Инициализируем обработчики только если элементы существуют
        const dateRangeForm = document.getElementById('dateRangeForm');
        if (dateRangeForm) {
            dateRangeForm.addEventListener('submit', function(e) {
                e.preventDefault();
                updateStatistics();
            });
        }

        const resetButton = document.getElementById('resetDates');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                resetDateRange();
            });
        }
    }
});

function createCourierRow(courier, index) {
    return `
        <td>${index + 1}</td>
        <td>${courier.full_name}</td>
        <td>${courier.phone}</td>
        <td>
            <span class="badge ${getOnboardingStatusBadgeClass(courier.onboarding_status)}">
                ${getOnboardingStatusText(courier.onboarding_status)}
            </span>
        </td>
        <td>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="viewCourier(${courier.id})" title="Просмотр">
                    <i class="fas fa-eye"></i>
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="editCourier(${courier.id})" title="Редактировать">
                    <i class="fas fa-edit"></i>
                </button>
                ${(courier.onboarding_status === 'IN_PROGRESS' || courier.onboarding_status === 'REJECTED_BY_COURIER') ? `
                    <button type="button" class="btn btn-sm btn-outline-success" onclick="verifyCourier(${courier.id})" title="Подтвердить">
                        <i class="fas fa-check"></i>
                    </button>
                ` : ''}
            </div>
        </td>
    `;
}

// Добавляем функцию для перевода статусов онбординга
function translateOnboardingStatus(status) {
    const statusMap = {
        'IN_PROGRESS': 'В процессе',
        'VERIFIED': 'Оформлен',
        'REJECTED_BY_HUB': 'Отказ хаба',
        'REJECTED_BY_COURIER': 'Отказ курьера'
    };
    return statusMap[status] || status;
}

async function loadCouriers() {
    try {
        const response = await fetch('/api/onboarding/couriers');
        const couriers = await response.json();
        
        const tbody = document.getElementById('couriersTableBody');
        tbody.innerHTML = '';
        
        couriers.forEach((courier, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${courier.full_name}</td>
                <td>${courier.phone}</td>
                <td>
                    <span class="badge ${getOnboardingStatusBadgeClass(courier.onboarding_status)}">
                        ${translateOnboardingStatus(courier.onboarding_status)}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="viewCourier(${courier.id})" title="Просмотр">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="editCourier(${courier.id})" title="Редактировать">
                            <i class="fas fa-edit"></i>
                        </button>
                        ${(courier.onboarding_status === 'IN_PROGRESS' || courier.onboarding_status === 'REJECTED_BY_COURIER') ? `
                            <button type="button" class="btn btn-sm btn-outline-success" onclick="verifyCourier(${courier.id})" title="Подтвердить">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка при загрузке курьеров:', error);
        showError('Ошибка при загрузке списка курьеров');
    }
}

function getOnboardingStatusText(status) {
    const statusMap = {
        'IN_PROGRESS': 'Оформляется',
        'VERIFIED': 'Оформлен',
        'REJECTED_BY_HUB': 'Отказ хаба',
        'REJECTED_BY_COURIER': 'Отказ курьера'
    };
    return statusMap[status] || 'Не определен';
}

function getOnboardingStatusBadgeClass(status) {
    const statusClasses = {
        'IN_PROGRESS': 'bg-warning',    // Желтый для "Оформляется"
        'VERIFIED': 'bg-success',       // Зеленый для "Оформлен"
        'REJECTED_BY_HUB': 'bg-danger', // Красный для отказов
        'REJECTED_BY_COURIER': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

// Обработчик изменения типа транспорта
function handleTransportTypeChange() {
    const transportType = document.getElementById('transportType').value;
    const vehicleFields = document.getElementById('vehicleFields');
    const vehicleModelField = document.getElementById('vehicleModelField');
    
    if (transportType === 'auto' || transportType === 'moto') {
        vehicleFields.style.display = 'block';
        vehicleModelField.style.display = transportType === 'auto' ? 'block' : 'none';
    } else {
        vehicleFields.style.display = 'none';
        vehicleModelField.style.display = 'none';
    }
}

// Функция для редактирования курьера
async function editCourier(id) {
    try {
        const response = await fetch(`/api/couriers/${id}`);
        const courier = await response.json();
        
        // Заполняем форму данными
        document.getElementById('editCourierId').value = courier.id;
        document.getElementById('editFullName').value = courier.full_name;
        document.getElementById('editPhone').value = courier.phone;
        document.getElementById('editTransportType').value = courier.transport_type;
        document.getElementById('editOnboardingStatus').value = courier.onboarding_status;
        
        // Обрабатываем поля транспорта
        const transportType = courier.transport_type;
        const vehicleFields = document.getElementById('editVehicleFields');
        const vehicleModelField = document.getElementById('editVehicleModelField');
        
        if (transportType === 'auto' || transportType === 'moto') {
            vehicleFields.style.display = 'block';
            document.getElementById('editVehicleNumber').value = courier.vehicle_number || '';
            document.getElementById('editDocumentsStatus').value = courier.documents_status || 'OK';
            
            if (transportType === 'auto') {
                vehicleModelField.style.display = 'block';
                document.getElementById('editVehicleModel').value = courier.vehicle_model || '';
            } else {
                vehicleModelField.style.display = 'none';
            }
        } else {
            vehicleFields.style.display = 'none';
            vehicleModelField.style.display = 'none';
        }
        
        // Показываем модальное окно
        const modal = new bootstrap.Modal(document.getElementById('editCourierModal'));
        modal.show();
    } catch (error) {
        console.error('Ошибка при загрузке данных курьера:', error);
        showError('Ошибка при загрузке данных курьера');
    }
}

// Обработчик изменения типа транспорта
document.getElementById('editTransportType').addEventListener('change', function() {
    const transportType = this.value;
    const vehicleFields = document.getElementById('editVehicleFields');
    const vehicleModelField = document.getElementById('editVehicleModelField');
    
    if (transportType === 'auto' || transportType === 'moto') {
        vehicleFields.style.display = 'block';
        vehicleModelField.style.display = transportType === 'auto' ? 'block' : 'none';
    } else {
        vehicleFields.style.display = 'none';
        vehicleModelField.style.display = 'none';
    }
});

// Функция сохранения изменений
async function saveEditCourier() {
    try {
        const id = document.getElementById('editCourierId').value;
        const data = {
            full_name: document.getElementById('editFullName').value,
            phone: document.getElementById('editPhone').value,
            transport_type: document.getElementById('editTransportType').value,
            onboarding_status: document.getElementById('editOnboardingStatus').value
        };

        // Добавляем поля транспорта если нужно
        if (data.transport_type === 'auto' || data.transport_type === 'moto') {
            data.vehicle_number = document.getElementById('editVehicleNumber').value;
            data.documents_status = document.getElementById('editDocumentsStatus').value;
            
            if (data.transport_type === 'auto') {
                data.vehicle_model = document.getElementById('editVehicleModel').value;
            }
        }

        const response = await fetch(`/api/couriers/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Ошибка при сохранении данных');
        }

        // Закрываем модальное окно
        const modal = bootstrap.Modal.getInstance(document.getElementById('editCourierModal'));
        modal.hide();

        // Обновляем список курьеров
        await loadCouriers();
        showSuccess('Данные курьера успешно обновлены');
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Ошибка при сохранении данных курьера');
    }
}

// Обновляем функцию verifyCourier
async function verifyCourier(id) {
    try {
        if (!confirm('Вы уверены, что хотите подтвердить этого курьера?')) {
            return;
        }

        const response = await fetch(`/api/onboarding/couriers/${id}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при подтверждении курьера');
        }

        await loadCouriers(); // Перезагружаем список
        showSuccess('Курьер успешно подтвержден');
    } catch (error) {
        console.error('Ошибка:', error);
        showError(error.message);
    }
}

// Функция для отображения сообщения об успехе
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show';
    successDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(successDiv, container.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
} 