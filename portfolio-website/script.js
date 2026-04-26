document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Example of a simple interactive element (can be expanded)
    const heroButton = document.querySelector('#hero .btn');
    if (heroButton) {
        heroButton.addEventListener('mouseover', () => {
            console.log('Hovering over "View My Work"');
            // Add more interactive effects here if desired
        });
    }

    // Form submission (placeholder for now)
    const contactForm = document.querySelector('#contact form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! (This is a demo)');
            this.reset(); // Clear the form
        });
    }
});