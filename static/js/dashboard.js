document.querySelectorAll('.dashboard-child').forEach(item => {
    item.addEventListener('click', function () {
        document.querySelectorAll('.dashboard-child')
                .forEach(el => el.classList.remove('active'));

        this.classList.add('active');
    });
});
