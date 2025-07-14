// Futuristic Spotify Wrapped Interactions
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize particle background
    createParticleBackground();
    
    // Add interactive card effects
    initializeCardInteractions();
    
    // Add smooth scrolling with parallax
    initializeScrollEffects();
    
    // Add typing animation for text elements
    initializeTypingAnimations();
    
    // Add audio visualization effects
    initializeAudioVisualizations();
});

// Create animated particle background
function createParticleBackground() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-bg';
    document.body.appendChild(particleContainer);
    
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
        particleContainer.appendChild(particle);
    }
}

// Enhanced card interactions
function initializeCardInteractions() {
    const cards = document.querySelectorAll('.spotify-card');
    
    cards.forEach(card => {
        // Add mouse tracking for 3D effect
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
        });
        
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
        
        // Add click ripple effect
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            const rect = card.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: radial-gradient(circle, rgba(29,185,84,0.3) 0%, transparent 70%);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
                z-index: 1000;
            `;
            
            card.style.position = 'relative';
            card.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Smooth scrolling effects (parallax removed to prevent floating cards)
function initializeScrollEffects() {
    // Parallax effects removed to prevent cards from floating on scroll
    // This was causing the "Your music universe" card and other cards to appear/disappear
    // and create empty spaces in the layout
    console.log('Scroll effects initialized without parallax to prevent floating cards');
}

// Typing animation for text elements
function initializeTypingAnimations() {
    const textElements = document.querySelectorAll('h1, h2, h3');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                typeText(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    textElements.forEach(element => {
        observer.observe(element);
    });
}

function typeText(element) {
    const text = element.textContent;
    element.textContent = '';
    element.style.borderRight = '2px solid #1DB954';
    
    let i = 0;
    const timer = setInterval(() => {
        element.textContent += text.charAt(i);
        i++;
        
        if (i >= text.length) {
            clearInterval(timer);
            setTimeout(() => {
                element.style.borderRight = 'none';
            }, 500);
        }
    }, 50);
}

// Audio visualization effects
function initializeAudioVisualizations() {
    const audioCards = document.querySelectorAll('[id*="audio"], [id*="track"], [id*="artist"]');
    
    audioCards.forEach(card => {
        // Add pulsing effect based on "audio activity"
        setInterval(() => {
            if (Math.random() > 0.7) {
                card.style.boxShadow = '0 0 30px rgba(29, 185, 84, 0.6)';
                setTimeout(() => {
                    card.style.boxShadow = '';
                }, 200);
            }
        }, 1000);
    });
}

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .spotify-card {
        transition: transform 0.1s ease-out;
    }
    
    .typing-cursor {
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
`;
document.head.appendChild(style);

// Enhanced loading states
function showLoadingState(element) {
    element.classList.add('loading-shimmer');
    element.style.pointerEvents = 'none';
}

function hideLoadingState(element) {
    element.classList.remove('loading-shimmer');
    element.style.pointerEvents = 'auto';
}

// Intersection Observer for animations
const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, { threshold: 0.1 });

// Observe all cards for entrance animations
document.querySelectorAll('.spotify-card').forEach(card => {
    animationObserver.observe(card);
});

// Add keyboard navigation support
document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        document.body.classList.add('keyboard-navigation');
    }
});

document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
});

// Performance optimization: Debounce resize events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

window.addEventListener('resize', debounce(() => {
    // Recalculate card positions and effects
    initializeCardInteractions();
}, 250));
