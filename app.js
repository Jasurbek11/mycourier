const PORT = process.env.PORT || 3000; // Укажите ваш порт
app.listen(PORT, () => {
    console.log(`Сервер запущен на http://localhost:${PORT}`);
    console.log('Ссылка на проект: http://ваш_проект.com'); // Добавлено
}); 