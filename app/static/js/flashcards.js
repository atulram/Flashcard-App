// Flashcard study functionality

class FlashcardStudy {
    constructor(flashcards, totalCards) {
        this.flashcards = flashcards;
        this.totalCards = totalCards;
        this.currentIndex = 0;
        this.isFlipped = false;
        
        this.initializeElements();
        this.setupEventListeners();
        this.updateCard();
        this.updateProgress();
        this.populateCardsList();
    }
    
    initializeElements() {
        this.flashcard = document.getElementById('flashcard');
        this.cardInner = document.getElementById('cardInner');
        this.questionContent = document.getElementById('questionContent');
        this.answerContent = document.getElementById('answerContent');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.completionScreen = document.getElementById('completionScreen');
        this.sidebar = document.getElementById('sidebar');
        this.cardsList = document.getElementById('cardsList');
    }
    
    setupEventListeners() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch(e.code) {
                case 'Space':
                    e.preventDefault();
                    this.flipCard();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousCard();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextCard();
                    break;
                case 'Escape':
                    this.closeSidebar();
                    break;
            }
        });
        
        // Touch gestures for mobile
        let startX = 0;
        let startY = 0;
        
        this.flashcard.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        this.flashcard.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Check if it's a horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (deltaX > 0) {
                    this.previousCard();
                } else {
                    this.nextCard();
                }
            }
            
            startX = 0;
            startY = 0;
        }, { passive: true });
    }
    
    flipCard() {
        this.isFlipped = !this.isFlipped;
        this.flashcard.classList.toggle('flipped', this.isFlipped);
        
        // Add ripple effect
        this.addRippleEffect();
    }
    
    addRippleEffect() {
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            width: 100px;
            height: 100px;
            left: 50%;
            top: 50%;
            margin-left: -50px;
            margin-top: -50px;
            z-index: 10;
        `;
        
        this.flashcard.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    nextCard() {
        if (this.currentIndex < this.totalCards - 1) {
            this.currentIndex++;
            this.updateCard();
            this.updateProgress();
            this.updateCardsList();
        } else {
            this.showCompletion();
        }
    }
    
    previousCard() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateCard();
            this.updateProgress();
            this.updateCardsList();
        }
    }
    
    goToCard(index) {
        if (index >= 0 && index < this.totalCards) {
            this.currentIndex = index;
            this.updateCard();
            this.updateProgress();
            this.updateCardsList();
            this.closeSidebar();
        }
    }
    
    updateCard() {
        const card = this.flashcards[this.currentIndex];
        
        // Reset flip state
        this.isFlipped = false;
        this.flashcard.classList.remove('flipped');
        
        // Update content with fade effect
        this.fadeAndUpdate(() => {
            this.questionContent.textContent = card.question;
            this.answerContent.textContent = card.answer;
        });
        
        // Update navigation buttons
        this.prevBtn.disabled = this.currentIndex === 0;
        this.nextBtn.disabled = this.currentIndex === this.totalCards - 1;
        
        if (this.currentIndex === this.totalCards - 1) {
            this.nextBtn.textContent = 'Finish';
        } else {
            this.nextBtn.textContent = 'Next →';
        }
    }
    
    fadeAndUpdate(updateFunction) {
        this.flashcard.style.opacity = '0.7';
        this.flashcard.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            updateFunction();
            this.flashcard.style.opacity = '1';
            this.flashcard.style.transform = 'scale(1)';
        }, 150);
    }
    
    updateProgress() {
        const progress = ((this.currentIndex + 1) / this.totalCards) * 100;
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = `${this.currentIndex + 1} / ${this.totalCards}`;
    }
    
    populateCardsList() {
        this.cardsList.innerHTML = '';
        
        this.flashcards.forEach((card, index) => {
            const cardItem = document.createElement('div');
            cardItem.className = 'card-item';
            if (index === this.currentIndex) {
                cardItem.classList.add('current');
            }
            
            cardItem.innerHTML = `
                <div class="card-item-question">${this.truncateText(card.question, 60)}</div>
                <div class="card-item-answer">${this.truncateText(card.answer, 80)}</div>
            `;
            
            cardItem.addEventListener('click', () => this.goToCard(index));
            this.cardsList.appendChild(cardItem);
        });
    }
    
    updateCardsList() {
        const cardItems = this.cardsList.querySelectorAll('.card-item');
        cardItems.forEach((item, index) => {
            item.classList.toggle('current', index === this.currentIndex);
        });
        
        // Scroll current item into view
        const currentItem = this.cardsList.querySelector('.card-item.current');
        if (currentItem) {
            currentItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }
    
    showCompletion() {
        this.completionScreen.style.display = 'flex';
        
        // Add celebration animation
        this.addCelebrationEffect();
    }
    
    addCelebrationEffect() {
        // Create confetti effect
        for (let i = 0; i < 30; i++) {
            setTimeout(() => {
                this.createConfetti();
            }, i * 100);
        }
    }
    
    createConfetti() {
        const confetti = document.createElement('div');
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        
        confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${randomColor};
            left: ${Math.random() * 100}vw;
            top: -10px;
            border-radius: 50%;
            animation: confetti-fall 3s linear forwards;
            z-index: 1001;
            pointer-events: none;
        `;
        
        document.body.appendChild(confetti);
        
        setTimeout(() => {
            confetti.remove();
        }, 3000);
    }
    
    restart() {
        this.currentIndex = 0;
        this.isFlipped = false;
        this.completionScreen.style.display = 'none';
        this.updateCard();
        this.updateProgress();
        this.updateCardsList();
    }
}

// Global functions for template
function initializeStudySession(flashcards, totalCards) {
    window.studySession = new FlashcardStudy(flashcards, totalCards);
}

function flipCard() {
    if (window.studySession) {
        window.studySession.flipCard();
    }
}

function nextCard() {
    if (window.studySession) {
        window.studySession.nextCard();
    }
}

function previousCard() {
    if (window.studySession) {
        window.studySession.previousCard();
    }
}

function restartStudy() {
    if (window.studySession) {
        window.studySession.restart();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.remove('open');
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes confetti-fall {
        to {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    .flashcard {
        transition: opacity 0.3s ease, transform 0.3s ease;
    }
`;
document.head.appendChild(style);

// Initialize tooltips and enhance user experience
document.addEventListener('DOMContentLoaded', () => {
    // Add keyboard shortcuts info
    const keyboardInfo = document.createElement('div');
    keyboardInfo.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; background: rgba(0,0,0,0.8); color: white; padding: 10px; border-radius: 5px; font-size: 12px; z-index: 1000;">
            <div><strong>Keyboard Shortcuts:</strong></div>
            <div>SPACE - Flip card</div>
            <div>← → - Navigate</div>
            <div>ESC - Close sidebar</div>
        </div>
    `;
    
    // Show keyboard info for 5 seconds
    document.body.appendChild(keyboardInfo);
    setTimeout(() => {
        keyboardInfo.style.opacity = '0';
        keyboardInfo.style.transition = 'opacity 1s';
        setTimeout(() => keyboardInfo.remove(), 1000);
    }, 5000);
});