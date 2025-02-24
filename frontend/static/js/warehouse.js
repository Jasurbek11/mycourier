// Загрузить список оборудования
async function loadEquipment() {
    try {
        const response = await fetch('/api/warehouse/equipment/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const equipment = await response.json();
            const tbody = document.getElementById('equipmentTableBody');
            tbody.innerHTML = '';
            
            equipment.forEach(item => {
                tbody.innerHTML += `
                    <tr>
                        <td>${item.id}</td>
                        <td>${item.name}</td>
                        <td>${item.serial_number}</td>
                        <td>${item.status}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" 
                                    onclick="assignEquipment(${item.id})">
                                Назначить
                            </button>
                        </td>
                    </tr>
                `;
            });
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Показать модальное окно добавления оборудования
function showAddEquipmentForm() {
    const modal = new bootstrap.Modal(document.getElementById('addEquipmentModal'));
    modal.show();
}

// Добавить новое оборудование
async function addEquipment(event) {
    event.preventDefault();
    
    const equipmentData = {
        name: document.getElementById('name').value,
        serial_number: document.getElementById('serialNumber').value
    };
    
    try {
        const response = await fetch('/api/warehouse/equipment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(equipmentData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            const errorDiv = document.getElementById('formError');
            errorDiv.textContent = errorData.detail || 'Ошибка при добавлении оборудования';
            errorDiv.style.display = 'block';
            return;
        }

        // Закрыть модальное окно и обновить список
        bootstrap.Modal.getInstance(document.getElementById('addEquipmentModal')).hide();
        document.getElementById('addEquipmentForm').reset();
        loadEquipment();
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка сервера');
    }
}

// Назначить оборудование курьеру
async function assignEquipment(equipmentId) {
    // TODO: Реализовать назначение оборудования
    alert('Функция назначения оборудования будет добавлена позже');
}

// Загрузить оборудование при загрузке страницы
document.addEventListener('DOMContentLoaded', loadEquipment); 