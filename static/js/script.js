// Toggle Course (Livello 1) - FILTRA I CONTENUTI
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
        // Se clicco di nuovo per chiudere, mostra tutto
        showAllContent();
    }
}

// Toggle Module (Livello 2) - FILTRA I CONTENUTI
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

// Funzione per filtrare i contenuti
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

// Funzione per mostrare tutti i contenuti
function showAllContent() {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.display = 'block';
    });
}

// Toggle Form (mostra/nascondi form di modifica)
function toggleForm(formId) {
    const form = document.getElementById(formId);
    if (form.style.display === 'none' || !form.style.display) {
        form.style.display = 'flex';
    } else {
        form.style.display = 'none';
    }
}

// Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Click sul logo "MCU" per mostrare tutto
    const logoArea = document.querySelector('.logo-area');
    if (logoArea) {
        logoArea.style.cursor = 'pointer';
        logoArea.addEventListener('click', function() {
            showAllContent();
            // Chiudi tutti i menu
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
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {
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
    
    // Lesson item click - scroll to card
    const lessonItems = document.querySelectorAll('.lesson-item');
    lessonItems.forEach(item => {
        item.addEventListener('click', function() {
            const lezioneId = this.getAttribute('data-lezione-id');
            const card = document.querySelector(`[data-lezione-id="${lezioneId}"]`);
            if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                card.style.boxShadow = '0 0 0 3px var(--accent-orange)';
                setTimeout(() => {
                    card.style.boxShadow = '';
                }, 2000);
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(400px)';
            setTimeout(() => alert.remove(), 300);
        });
    }, 5000);
});