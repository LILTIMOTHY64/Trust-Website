// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    const carouselInner = document.querySelector('.carousel-inner');
    const items = document.querySelectorAll('.carousel-item');
    let currentIndex = 0;
    const totalItems = items.length;

    function showNextItem() {
        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
    }

    function showPrevItem() {
        currentIndex = (currentIndex - 1 + totalItems) % totalItems;
        updateCarousel();
    }

    function updateCarousel() {
        const offset = -currentIndex * 100;
        carouselInner.style.transform = `translateX(${offset}%)`;
    }

    document.querySelector('.carousel-control-next').addEventListener('click', showNextItem);
    document.querySelector('.carousel-control-prev').addEventListener('click', showPrevItem);

    setInterval(showNextItem, 3000); // Auto-scroll every 3 seconds
});
