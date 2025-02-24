// Глобальная переменка для отслеживания состояния авторизации
// let isAuthChecking = false;

function addAuthorizationHeader(headers = {}) {
    const token = localStorage.getItem('token');
    if (token) {
        return {
            ...headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return headers;
}

// Глобальный перехватчик fetch
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    options = options || {};
    options.headers = options.headers || {};
    
    const token = localStorage.getItem('token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    options.credentials = 'include';
    
    return originalFetch(url, options);
};

async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
            credentials: 'include'
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка при входе');
        }

        // Сохраняем токен без префикса Bearer
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Делаем редирект
        window.location.href = data.redirect_url;

    } catch (error) {
        console.error('Login error:', error);
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

// Обработка клика по логотипу
document.addEventListener('DOMContentLoaded', function() {
    const brandLink = document.querySelector('.navbar-brand');
    if (brandLink) {
        brandLink.addEventListener('click', function(e) {
            e.preventDefault();
            const token = localStorage.getItem('token');
            if (token) {
                // Проверяем роль пользователя
                fetch('/api/auth/me', {
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.role === 'onboarding') {
                        window.location.href = '/onboarding';
                    } else if (data.role === 'warehouse') {
                        window.location.href = '/warehouse';
                    }
                })
                .catch(() => {
                    window.location.href = '/login';
                });
            } else {
                window.location.href = '/login';
            }
        });
    }
});

// Функция для проверки авторизации
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && window.location.pathname !== '/login') {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Проверяем авторизацию при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Пропускаем проверку только для страницы логина
    if (!window.location.pathname.includes('/login')) {
        checkAuth();
    }
});

// Функция выхода
async function logout() {
    try {
        const token = localStorage.getItem('token');
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            credentials: 'include'
        });
    } finally {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        window.location.href = '/login';
    }
}