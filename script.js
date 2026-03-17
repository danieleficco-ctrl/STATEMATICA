function toggleCourse(element) {
    const courseItem = element.parentElement;
    const courseId = courseItem.getAttribute('data-corso-id');
    const isActive = courseItem.classList.contains('active');
    
    // Chiudi tutti gli altri corsi
    document.querySelectorAll('.course-item').forEach(item => {
        if (item !== courseItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle active state
    courseItem.classList.toggle('active');
    
    // Se sto attivando questo corso, filtralo
    if (!isActive && courseId) {
        filterContent('corso', courseId);
    } else if (isActive) {
        showAllContent();
    }
}

function toggleModule(element) {
    const moduleItem = element.parentElement;
    const moduleId = moduleItem.getAttribute('data-modulo-id');
    const isActive = moduleItem.classList.contains('active');
    
    // Toggle active state
    moduleItem.classList.toggle('active');
    
    // Se sto attivando questo modulo, filtralo
    if (!isActive && moduleId) {
        filterContent('modulo', moduleId);
    }
}

function filterContent(tipo, id) {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        if (tipo === 'corso') {
            const cardCorsoId = card.getAttribute('data-corso-id');
            card.style.display = (cardCorsoId === id) ? 'block' : 'none';
        } else if (tipo === 'modulo') {
            const cardModuloId = card.getAttribute('data-modulo-id');
            card.style.display = (cardModuloId === id) ? 'block' : 'none';
        } else if (tipo === 'lezione') {
            const cardLezioneId = card.getAttribute('data-lezione-id');
            card.style.display = (cardLezioneId === id) ? 'block' : 'none';
        }
    });
}

function showAllContent() {
    document.querySelectorAll('.card').forEach(card => {
        card.style.display = 'block';
    });
}

// Click sul logo MCU per mostrare tutto
document.addEventListener('DOMContentLoaded', function() {
    const logoArea = document.querySelector('.logo-area');
    if (logoArea) {
        logoArea.style.cursor = 'pointer';
        logoArea.addEventListener('click', function() {
            showAllContent();
            document.querySelectorAll('.course-item.active, .module-item.active').forEach(item => {
                item.classList.remove('active');
            });
        });
    }
    
    // Search functionality
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