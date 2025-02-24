let loadingTimeout;
const loadingDelay = 300; // Задержка перед показом индикатора загрузки

function showLoading() {
    const existing = document.querySelector('.loading-overlay');
    if (existing) return;
    
    const loader = document.createElement('div');
    loader.className = 'loading-overlay';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => loader.remove(), 300);
    }
}

async function loadCouriers(page = 1) {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('No token found');
            window.location.href = '/login';
            return;
        }

        const response = await fetch(`/api/onboarding/couriers?page=${page}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Пробуем получить токен из cookie
                const cookies = document.cookie.split(';');
                const tokenCookie = cookies.find(c => c.trim().startsWith('access_token='));
                if (tokenCookie) {
                    const cookieToken = tokenCookie.split('=')[1].trim();
                    // Сохраняем токен в localStorage без префикса Bearer
                    localStorage.setItem('token', cookieToken.replace('Bearer ', ''));
                    // Повторяем запрос
                    return loadCouriers(page);
                }
                window.location.href = '/login';
                return;
            }
            throw new Error('Failed to load couriers');
        }

        const data = await response.json();
        const tableBody = document.getElementById('couriersTableBody');
        if (!tableBody) return;

        if (!data.items || data.items.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Нет курьеров</td></tr>';
            return;
        }

        tableBody.innerHTML = '';
        data.items.forEach((courier, index) => {
            const row = createCourierRow(courier, index + 1);
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading couriers:', error);
        const tableBody = document.getElementById('couriersTableBody');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        Ошибка при загрузке списка курьеров: ${error.message}
                    </td>
                </tr>
            `;
        }
    }
}

// Функция для закрытия модального окна
function closeModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

// Функция для создания строки таблицы
function createCourierRow(courier, index, page) {
    const row = document.createElement('tr');
    const statusBadgeClass = getOnboardingStatusBadgeClass(courier.onboarding_status);
    const statusText = translateOnboardingStatus(courier.onboarding_status);

    row.innerHTML = `
        <td>${(page - 1) * 10 + index + 1}</td>
        <td>${courier.full_name}</td>
        <td>${courier.phone}</td>
        <td>
            <span class="badge ${statusBadgeClass}">${statusText}</span>
        </td>
        <td>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-info" onclick="viewCourier(${courier.id})" title="Просмотр">
                    <i class="bi bi-eye"></i>
                </button>
                <button type="button" class="btn btn-sm btn-primary" onclick="editCourier(${courier.id})" title="Редактировать">
                    <i class="bi bi-pencil"></i>
                </button>
                ${(courier.onboarding_status === 'WILL_BE_VERIFIED' || courier.onboarding_status === 'REJECTED_BY_COURIER') ? `
                    <button type="button" class="btn btn-sm btn-success" onclick="verifyCourier(${courier.id})" title="Изменить статус на 'Оформлен'">
                        <i class="bi bi-check-lg"></i>
                    </button>
                ` : ''}
            </div>
        </td>
    `;

    return row;
}

// В начале файла добавим инициализацию модальных окон
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация модальных окон Bootstrap
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        new bootstrap.Modal(modal);
    });

    // Добавляем обработчик для формы
    const addForm = document.getElementById('addCourierForm');
    if (addForm) {
        addForm.addEventListener('submit', handleAddCourier);
    }

    // Загрузка курьеров при загрузке страницы
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('No token found on page load');
        window.location.href = '/login';
        return;
    }
    loadCouriers();
});

// Обновляем функцию handleAddCourier
async function handleAddCourier(event) {
    event.preventDefault();
    const submitButton = document.querySelector('#addCourierModal .btn-primary');
    const form = event.target; // Получаем форму из события
    const modalElement = document.getElementById('addCourierModal');
    const modal = bootstrap.Modal.getInstance(modalElement);
    
    try {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Создание...';

        const formData = new FormData(form);
        
        // Форматируем телефон
        let phone = formData.get('phone').trim();
        if (!phone.startsWith('+')) {
            phone = '+' + phone;
        }
        
        const data = {
            full_name: formData.get('full_name').trim(),
            phone: phone,
            pinfl: formData.get('pinfl').trim(),
            transport_type: formData.get('transport_type'),
            vehicle_number: formData.get('vehicle_number')?.trim() || null,
            vehicle_model: formData.get('vehicle_model')?.trim() || null
        };

        const response = await fetch('/api/onboarding/couriers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Ошибка при создании курьера');
        }

        // Закрываем модальное окно
        if (modal) {
            modal.hide();
        }
        
        // Очищаем форму
        form.reset();

        // Обновляем список курьеров
        await loadCouriers(1);
        showSuccess('Курьер успешно добавлен');

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Ошибка при создании курьера');
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Создать';
    }
}

// Обработчик изменения типа транспорта
function handleTransportTypeChange(selectElement, prefix = '') {
    const vehicleFields = document.getElementById((prefix || 'add') + 'VehicleFields');
    const vehicleModelField = document.getElementById((prefix || 'add') + 'VehicleModelField');
    const vehicleDocsField = document.getElementById((prefix || 'add') + 'VehicleDocsField');

    if (selectElement.value === 'auto' || selectElement.value === 'moto') {
        vehicleFields.style.display = 'block';
        vehicleDocsField.style.display = 'block';  // Всегда показываем статус документов
        
        if (vehicleModelField) {
            vehicleModelField.style.display = selectElement.value === 'auto' ? 'block' : 'none';
        }
    } else {
        vehicleFields.style.display = 'none';
    }
}

// Инициализация обработчиков для модальных окон
function initializeModalHandlers(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const prefix = modalId === 'addCourierModal' ? '' : 'edit';
    const transportType = document.getElementById(prefix + 'TransportType');
    
    if (transportType) {
        // Вызываем обработчик для начальной инициализации
        handleTransportTypeChange(transportType, prefix);
        
        // Добавляем обработчик изменений
        transportType.addEventListener('change', function() {
            handleTransportTypeChange(this, prefix);
        });
    }
}

// Глобальный перехватчик fetch
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    options = options || {};
    options.headers = options.headers || {};
    
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    } else {
        // Пробуем получить токен из cookie
        const cookies = document.cookie.split(';');
        const tokenCookie = cookies.find(c => c.trim().startsWith('access_token='));
        if (tokenCookie) {
            const cookieToken = tokenCookie.split('=')[1].trim();
            // Сохраняем токен в localStorage без префикса Bearer
            const token = cookieToken.replace('Bearer ', '');
            localStorage.setItem('token', token);
            options.headers['Authorization'] = `Bearer ${token}`;
        }
    }
    
    options.credentials = 'include';
    
    return originalFetch(url, options);
};

// Функция для перевода статусов онбординга
function translateOnboardingStatus(status) {
    const statuses = {
        'WILL_BE_VERIFIED': 'Оформится',
        'VERIFIED': 'Оформлен',
        'REJECTED_BY_HUB': 'Отказ хаба',
        'REJECTED_BY_COURIER': 'Отказ курьера'
    };
    return statuses[status] || status;
}

// Добавляем функцию для определения класса бейджа
function getOnboardingStatusBadgeClass(status) {
    const statusClasses = {
        'IN_PROGRESS': 'bg-warning',    // Желтый для "В процессе"
        'VERIFIED': 'bg-success',       // Зеленый для "Оформлен"
        'REJECTED_BY_HUB': 'bg-danger', // Красный для отказов
        'REJECTED_BY_COURIER': 'bg-danger'
    };
    return statusClasses[status] || 'bg-secondary';
}

// Добавляем функцию для отображения ошибок
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(errorDiv, container.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Функция для проверки необходимости показа кнопки подтверждения
function shouldShowVerifyButton(status) {
    // Показываем галочку только для статусов "Оформится" и "Отказ курьера"
    return status === 'WILL_BE_VERIFIED' || status === 'REJECTED_BY_COURIER';
}

// Функция для создания кнопок действий
function createActionButtons(courier) {
    const buttons = [];
    
    // Кнопка просмотра
    buttons.push(`<button class="btn btn-sm btn-info view-courier" data-courier-id="${courier.id}" title="Просмотр">
        <i class="bi bi-eye"></i>
    </button>`);
    
    // Кнопка редактирования
    buttons.push(`<button class="btn btn-sm btn-primary edit-courier" data-courier-id="${courier.id}" title="Редактировать">
        <i class="bi bi-pencil"></i>
    </button>`);
    
    // Кнопка подтверждения (галочка) - показываем для всех статусов, кроме "Оформлен" и "Отказ хаба"
    if (shouldShowVerifyButton(courier.onboarding_status)) {
        buttons.push(`<button class="btn btn-sm btn-success verify-courier" data-courier-id="${courier.id}" title="Изменить статус на 'Оформлен'">
            <i class="bi bi-check-lg"></i>
        </button>`);
    }
    
    return buttons.join(' ');
}

// Функция подтверждения курьера
async function verifyCourier(courierId) {
    try {
        if (!confirm('Вы уверены, что хотите изменить статус курьера на "Оформлен"?')) {
            return;
        }

        const response = await fetch(`/api/onboarding/couriers/${courierId}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.detail || 'Не удалось изменить статус курьера');
        }

        await loadCouriers();
        showSuccess('Статус курьера успешно изменен на "Оформлен"');
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
    }
}

// Вспомогательная функция для показа сообщения об успехе
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

// Функция для преобразования статуса документов в текст
function translateDocumentStatus(status) {
    const statusMap = {
        'NOT_VERIFIED': 'Не проверено',
        'VERIFIED': 'Проверено',
        'PROBLEM': 'Проблема с документами'
    };
    return statusMap[status] || status;
}

// Обновляем функцию просмотра курьера
async function viewCourier(id) {
    try {
        const response = await fetch(`/api/onboarding/couriers/${id}`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Ошибка при загрузке данных курьера');
        }

        const courier = await response.json();
        console.log('Loaded courier data:', courier);

        // Заполняем основную информацию
        document.getElementById('viewFullName').textContent = courier.full_name;
        document.getElementById('viewPhone').textContent = courier.phone;
        document.getElementById('viewPinfl').textContent = courier.pinfl;
        document.getElementById('viewTransportType').textContent = translateTransportType(courier.transport_type);
        document.getElementById('viewOnboardingStatus').textContent = translateOnboardingStatus(courier.onboarding_status);

        // Показываем/скрываем поля транспорта
        const vehicleFields = document.getElementById('viewVehicleFields');
        const vehicleModelField = document.getElementById('viewVehicleModelField');
        
        if (courier.transport_type === 'auto' || courier.transport_type === 'moto') {
            vehicleFields.style.display = 'block';
            document.getElementById('viewVehicleNumber').textContent = courier.vehicle_number || '-';
            document.getElementById('viewVehicleDocs').textContent = translateVehicleDocsStatus(courier.vehicle_docs_status);
            
            if (courier.transport_type === 'auto') {
                vehicleModelField.style.display = 'block';
                document.getElementById('viewVehicleModel').textContent = courier.vehicle_model || '-';
            } else {
                vehicleModelField.style.display = 'none';
            }
        } else {
            vehicleFields.style.display = 'none';
        }

        // Показываем модальное окно
        const viewModal = new bootstrap.Modal(document.getElementById('viewCourierModal'));
        viewModal.show();

        // Инициализируем вкладки
        const tabs = document.querySelectorAll('#courierTabs .nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('click', function(event) {
                event.preventDefault();
                const targetId = this.getAttribute('data-bs-target').replace('#', '');
                
                // Убираем активный класс у всех вкладок
                tabs.forEach(t => t.classList.remove('active'));
                // Добавляем активный класс текущей вкладке
                this.classList.add('active');
                
                // Скрываем все панели
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                
                // Показываем нужную панель
                const targetPane = document.getElementById(targetId);
                if (targetPane) {
                    targetPane.classList.add('show', 'active');
                    // Загружаем данные для вкладки
                    loadCourierHistory(id, targetId);
                }
            });
        });

        // Загружаем историю для первой вкладки
        loadCourierHistory(id, 'info');

    } catch (error) {
        console.error('Error:', error);
        showError('Ошибка при загрузке данных курьера');
    }
}

// Добавим также функцию для перевода типа транспорта
function translateTransportType(type) {
    const types = {
        'pedestrian': 'Пешком',
        'bicycle': 'Велосипед',
        'moto': 'Мотоцикл',
        'auto': 'Автомобиль'
    };
    return types[type] || type;
}

// Редактирование курьера
async function editCourier(id) {
    try {
        showLoading();
        console.log('Editing courier with ID:', id);

        const response = await fetch(`/api/onboarding/couriers/${id}`, {
            method: 'GET',
            credentials: 'include'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при загрузке данных курьера');
        }

        const courier = await response.json();
        console.log('Loaded courier data:', courier);

        // Сначала показываем модальное окно
        const editModal = new bootstrap.Modal(document.getElementById('editCourierModal'));
        editModal.show();

        // Ждем, пока модальное окно откроется
        await new Promise(resolve => setTimeout(resolve, 100));

        // Теперь заполняем форму
        const form = document.getElementById('editCourierForm');
        if (!form) {
            console.error('Form not found');
            throw new Error('Форма редактирования не найдена');
        }

        // Заполняем поля формы
        const fields = {
            'editCourierId': courier.id,
            'editFullName': courier.full_name,
            'editPhone': courier.phone,
            'editPinfl': courier.pinfl,
            'editTransportType': courier.transport_type,
            'editOnboardingStatus': courier.onboarding_status
        };

        // Устанавливаем значения
        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                // Вызываем событие change для select элементов
                if (element.tagName === 'SELECT') {
                    element.dispatchEvent(new Event('change'));
                }
            } else {
                console.warn(`Element with id ${id} not found`);
            }
        });

        // Обрабатываем поля транспорта
        const vehicleFields = document.getElementById('editVehicleFields');
        const vehicleModelField = document.getElementById('editVehicleModelField');
        
        if (courier.transport_type === 'auto' || courier.transport_type === 'moto') {
            vehicleFields.style.display = 'block';
            const vehicleNumber = document.getElementById('editVehicleNumber');
            if (vehicleNumber) {
                vehicleNumber.value = courier.vehicle_number || '';
            }
            
            if (courier.transport_type === 'auto') {
                vehicleModelField.style.display = 'block';
                const vehicleModel = document.getElementById('editVehicleModel');
                if (vehicleModel) {
                    vehicleModel.value = courier.vehicle_model || '';
                }
            } else {
                vehicleModelField.style.display = 'none';
            }
        } else {
            vehicleFields.style.display = 'none';
        }

        // Логируем установленные значения
        console.log('Form fields after setting values:', {
            id: document.getElementById('editCourierId')?.value,
            name: document.getElementById('editFullName')?.value,
            phone: document.getElementById('editPhone')?.value,
            pinfl: document.getElementById('editPinfl')?.value,
            transport: document.getElementById('editTransportType')?.value,
            status: document.getElementById('editOnboardingStatus')?.value
        });

    } catch (error) {
        console.error('Error in editCourier:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Функция обновления доступности полей в зависимости от статуса
function updateFieldsBasedOnStatus(status) {
    const transportFields = document.getElementById('editVehicleFields');
    const transportSelect = document.getElementById('editTransportType');
    
    // Если статус "Оформлен", блокируем все поля
    const isVerified = status === 'VERIFIED';
    transportSelect.disabled = isVerified;
    
    if (transportFields) {
        const inputs = transportFields.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.disabled = isVerified;
        });
    }
}

// Функция для обновления курьера
async function updateCourier(event) {
    event.preventDefault();
    const submitButton = document.querySelector('#editCourierModal .btn-primary');
    
    try {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Сохранение...';

        const form = document.getElementById('editCourierForm');
        const courierId = document.getElementById('editCourierId').value;
        
        // Получаем данные формы
        const data = {
            full_name: document.getElementById('editFullName').value.trim(),
            phone: document.getElementById('editPhone').value.trim(),
            pinfl: document.getElementById('editPinfl').value.trim(),
            transport_type: document.getElementById('editTransportType').value,
            onboarding_status: document.getElementById('editOnboardingStatus').value,
            vehicle_number: document.getElementById('editVehicleNumber')?.value.trim() || null,
            vehicle_model: document.getElementById('editVehicleModel')?.value.trim() || null
        };

        console.log('Sending update data:', data);

        const response = await fetch(`/api/onboarding/couriers/${courierId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            if (response.status === 422 && result.detail) {
                throw new Error(Array.isArray(result.detail) ? 
                    result.detail[0].msg : 
                    result.detail);
            }
            throw new Error(result.detail || 'Ошибка при обновлении данных курьера');
        }

        // Закрываем модальное окно
        const modal = bootstrap.Modal.getInstance(document.getElementById('editCourierModal'));
        modal.hide();
        
        // Обновляем список курьеров
        await loadCouriers();
        showSuccess('Данные курьера успешно обновлены');

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Ошибка при обновлении данных курьера');
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Сохранить';
    }
}

// Обновляем функцию загрузки истории
async function loadCourierHistory(id, type = 'onboarding') {
    // Пропускаем загрузку истории для вкладки основной информации
    if (type === 'info') return;

    try {
        const response = await fetch(`/api/onboarding/couriers/${id}/history`, {
            credentials: 'include'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка при загрузке истории');
        }

        const allHistory = await response.json();
        // Фильтруем историю по типу
        const history = allHistory.filter(record => record.type === type);
        
        const tableId = `${type}HistoryTable`;
        const tbody = document.getElementById(tableId);
        
        if (!tbody) {
            console.error(`Table body with id ${tableId} not found`);
            return;
        }

        tbody.innerHTML = '';

        if (history.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">История отсутствует</td></tr>`;
            return;
        }

        history.forEach(record => {
            let row = '<tr>';
            switch(type) {
                case 'onboarding':
                    row += `
                        <td>${new Date(record.created_at).toLocaleString()}</td>
                        <td>${record.event}</td>
                        <td>${record.user?.username || '-'}</td>
                        <td>${record.comment || '-'}</td>
                    `;
                    break;
                case 'activation':
                    row += `
                        <td>${new Date(record.created_at).toLocaleString()}</td>
                        <td>${record.event}</td>
                        <td>${record.user?.username || '-'}</td>
                        <td>${record.status || '-'}</td>
                    `;
                    break;
                case 'warehouse':
                    row += `
                        <td>${new Date(record.created_at).toLocaleString()}</td>
                        <td>${record.equipment_name || '-'}</td>
                        <td>${record.event}</td>
                        <td>${record.user?.username || '-'}</td>
                    `;
                    break;
                case 'accounting':
                    row += `
                        <td>${new Date(record.created_at).toLocaleString()}</td>
                        <td>${record.amount || '-'}</td>
                        <td>${record.status || '-'}</td>
                        <td>${record.comment || '-'}</td>
                    `;
                    break;
            }
            row += '</tr>';
            tbody.innerHTML += row;
        });

    } catch (error) {
        console.error(`Error loading ${type} history:`, error);
        const tbody = document.getElementById(`${type}HistoryTable`);
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">Ошибка при загрузке истории</td></tr>`;
        }
    }
}

// Функция обновления пагинации
function updatePagination(currentPage, totalPages) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;

    let html = '';
    
    // Кнопка "Предыдущая"
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadCouriers(${currentPage - 1})" ${currentPage === 1 ? 'tabindex="-1"' : ''}>
                Предыдущая
            </a>
        </li>
    `;

    // Номера страниц
    for (let i = 1; i <= totalPages; i++) {
        html += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadCouriers(${i})">${i}</a>
            </li>
        `;
    }

    // Кнопка "Следующая"
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadCouriers(${currentPage + 1})" ${currentPage === totalPages ? 'tabindex="-1"' : ''}>
                Следующая
            </a>
        </li>
    `;

    paginationContainer.innerHTML = html;
}

// Функция загрузки истории выплат
async function loadAccountingHistory(id) {
    try {
        const response = await fetch(`/api/onboarding/couriers/${id}/accounting`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Ошибка при загрузке истории выплат');
        }

        const history = await response.json();
        const tbody = document.getElementById('accountingHistoryTable');
        
        if (!tbody) {
            console.error('Accounting history table not found');
            return;
        }

        tbody.innerHTML = '';

        if (history.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">История выплат отсутствует</td></tr>`;
            return;
        }

        history.forEach(record => {
            tbody.innerHTML += `
                <tr>
                    <td>${new Date(record.created_at).toLocaleString()}</td>
                    <td>${record.amount}</td>
                    <td>${record.status}</td>
                    <td>${record.comment || '-'}</td>
                </tr>
            `;
        });

    } catch (error) {
        console.error('Error loading accounting history:', error);
        const tbody = document.getElementById('accountingHistoryTable');
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center">Ошибка при загрузке истории выплат</td></tr>`;
        }
    }
}

// Добавляем функцию поиска
async function searchCouriers() {
    const searchInput = document.getElementById('searchInput');
    const searchText = searchInput.value.trim();
    
    try {
        const response = await fetch(`/api/onboarding/couriers?search=${encodeURIComponent(searchText)}`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Ошибка при поиске курьеров');
        }

        const data = await response.json();
        console.log('Search results:', data); // Для отладки
        
        const tbody = document.getElementById('couriersTableBody');
        if (!tbody) {
            console.error('Couriers table body not found');
            return;
        }

        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Курьеры не найдены</td></tr>';
            return;
        }

        data.items.forEach(courier => {
            const statusBadgeClass = getOnboardingStatusBadgeClass(courier.onboarding_status);
            const statusText = translateOnboardingStatus(courier.onboarding_status);
            
            tbody.innerHTML += `
                <tr>
                    <td>${courier.full_name}</td>
                    <td>${courier.phone}</td>
                    <td>
                        <span class="badge ${statusBadgeClass}">${statusText}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info view-courier" data-courier-id="${courier.id}">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary edit-courier" data-courier-id="${courier.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        ${shouldShowVerifyButton(courier.onboarding_status) ? `
                            <button class="btn btn-sm btn-success verify-courier" data-courier-id="${courier.id}">
                                <i class="bi bi-check-lg"></i>
                            </button>
                        ` : ''}
                    </td>
                </tr>
            `;
        });

        // Обновляем пагинацию
        updatePagination(data.page, data.pages);

    } catch (error) {
        console.error('Failed to search couriers:', error);
        showError('Ошибка при поиске курьеров');
    }
}

function translateVehicleDocsStatus(status) {
    const statuses = {
        'NOT_VERIFIED': 'Не проверено',
        'VERIFIED': 'Проверено',
        'PROBLEM': 'Проблема с документами'
    };
    return statuses[status] || status;
}

// Добавляем функцию logout
async function logout() {
    try {
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include' // важно для работы с куки
        });

        if (response.ok) {
            // Удаляем куки и редиректим на страницу логина
            document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            window.location.href = '/login';
        } else {
            console.error('Ошибка при выходе из системы');
        }
    } catch (error) {
        console.error('Ошибка при выходе:', error);
    }
}