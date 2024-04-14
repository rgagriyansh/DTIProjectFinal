document.addEventListener('DOMContentLoaded', function() {
    const questions = document.querySelectorAll('.faq-item h3');
    
    questions.forEach(question => {
        question.addEventListener('click', function() {
            const faqItem = this.parentElement; // Select the parent faq-item element
            faqItem.classList.toggle('active'); // Toggle the 'active' class on the faq-item element
        });
    });
});
