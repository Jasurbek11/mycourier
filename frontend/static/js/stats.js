async function loadStats() {
    try {
        const response = await fetch('/api/onboarding/stats', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Stats data:', data);
        
        // Обновляем счетчики
        document.getElementById('total-couriers').textContent = data.total_couriers || 0;
        document.getElementById('active-couriers').textContent = data.active_couriers || 0;
        document.getElementById('inactive-couriers').textContent = data.inactive_couriers || 0;
        document.getElementById('blocked-couriers').textContent = data.blocked_couriers || 0;
        
        // Если есть данные по регистрациям, создаем график
        if (data.registrations && data.registrations.length > 0) {
            const ctx = document.getElementById('registrations-chart').getContext('2d');
            
            // Уничтожаем существующий график, если он есть
            const existingChart = Chart.getChart(ctx.canvas);
            if (existingChart) {
                existingChart.destroy();
            }
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.registrations.map(r => new Date(r.date).toLocaleDateString('ru')),
                    datasets: [{
                        label: 'Регистрации',
                        data: data.registrations.map(r => r.count),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
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
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Загружаем статистику при загрузке страницы
document.addEventListener('DOMContentLoaded', loadStats); 