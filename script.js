function toggleCourse(element) {
    const courseItem = element.parentElement;
    courseItem.classList.toggle('active');
}

function toggleModule(element) {
    const moduleItem = element.parentElement;
    moduleItem.classList.toggle('active');
}

function selectLesson(lezioneId) {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const cardLezioneId = card.getAttribute('data-lezione-id');
        if (cardLezioneId == lezioneId) {
            card.style.display = 'block';
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            card.style.display = 'none';
        }
    });
}

function showAllLessons() {
    document.querySelectorAll('.card').forEach(card => {
        card.style.display = 'block';
    });
}

// Click sul logo MCU per mostrare tutto
document.addEventListener('DOMContentLoaded', function() {
    const logoArea = document.querySelector('.logo-area');
    if (logoArea) {
        logoArea.addEventListener('click', showAllLessons);
    }
    
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            document.querySelectorAll('.card').forEach(card => {
                const corso = card.getAttribute('data-corso').toLowerCase();
                const modulo = card.getAttribute('data-modulo').toLowerCase();
                const titolo = card.getAttribute('data-titolo').toLowerCase();
                
                if (corso.includes(searchTerm) || modulo.includes(searchTerm) || titolo.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});