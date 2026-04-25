/**
 * Padel News Pro - Application Script
 * Premier Padel Tour 2026
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('🎾 Padel News Pro loaded');
  
  // Initialize ranking tabs
  initRankingTabs();
  
  // Initialize live score updates
  initLiveScores();
  
  // Initialize news card interactions
  initNewsCards();
  
  // Initialize calendar highlights
  highlightCurrentTournament();
});

/**
 * Ranking Tabs - Toggle between Men's and Women's rankings
 */
function initRankingTabs() {
  const tabs = document.querySelectorAll('.ranking-tab');
  const menRanking = document.getElementById('men-ranking');
  const womenRanking = document.getElementById('women-ranking');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Show/hide ranking content
      const targetTab = this.dataset.tab;
      
      if (targetTab === 'men') {
        menRanking.classList.remove('hidden');
        womenRanking.classList.add('hidden');
      } else {
        menRanking.classList.add('hidden');
        womenRanking.classList.remove('hidden');
      }
    });
  });
}

/**
 * Live Scores - Simulate live score updates for ongoing matches
 */
function initLiveScores() {
  // Check if we're on a page with live matches
  const liveMatches = document.querySelectorAll('.live-match');
  
  if (liveMatches.length > 0) {
    console.log('🔴 Live matches detected');
    
    // Update match status every 30 seconds (simulated)
    setInterval(() => {
      updateLiveMatchDisplay();
    }, 30000);
  }
}

function updateLiveMatchDisplay() {
  // In production, this would fetch real data from an API
  const liveIndicators = document.querySelectorAll('.live-indicator');
  
  liveIndicators.forEach(indicator => {
    // Add a subtle pulse effect
    indicator.style.animation = 'none';
    setTimeout(() => {
      indicator.style.animation = '';
    }, 10);
  });
}

/**
 * News Cards - Add hover effects and click handlers
 */
function initNewsCards() {
  const newsCards = document.querySelectorAll('.news-card');
  
  newsCards.forEach(card => {
    card.addEventListener('click', function() {
      // In production, this would navigate to the full article
      const title = this.querySelector('h3').textContent;
      console.log('📰 Article clicked:', title);
      
      // Add a subtle click effect
      this.style.transform = 'scale(0.98)';
      setTimeout(() => {
        this.style.transform = '';
      }, 150);
    });
  });
}

/**
 * Highlight current tournament in calendar
 */
function highlightCurrentTournament() {
  const tournamentCards = document.querySelectorAll('.tournament-card');
  const today = new Date();
  
  tournamentCards.forEach(card => {
    const dateText = card.querySelector('.tournament-date').textContent;
    const statusBadge = card.querySelector('.status-badge');
    
    if (statusBadge && statusBadge.textContent.includes('EN CURSO')) {
      card.classList.add('ongoing');
      card.style.borderLeftColor = '#ff6600';
    }
  });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('es-ES', options);
}

/**
 * Format score display
 */
function formatScore(score) {
  return score.replace(/(\d)-(\d)/g, '<strong>$1-$2</strong>');
}

/**
 * Get flag emoji from country code
 */
function getFlagEmoji(countryCode) {
  const codePoints = countryCode
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt());
  return String.fromCodePoint(...codePoints);
}

/**
 * Calculate tournament days remaining
 */
function getDaysRemaining(startDate) {
  const start = new Date(startDate);
  const today = new Date();
  const diff = start - today;
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

/**
 * Update ranking trends with animation
 */
function animateRankingTrends() {
  const trends = document.querySelectorAll('.trend');
  
  trends.forEach(trend => {
    const trendText = trend.textContent;
    
    if (trendText === '⬆️') {
      trend.style.color = '#00cc99';
    } else if (trendText === '⬇️') {
      trend.style.color = '#ff6600';
    } else if (trendText === '🆕') {
      trend.style.color = '#0066cc';
    }
  });
}

// Run trend animation on load
setTimeout(animateRankingTrends, 500);

/**
 * Smooth scroll to section
 */
function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

/**
 * Load more news articles (pagination)
 */
function loadMoreNews() {
  // In production, this would fetch more articles from an API
  console.log('📰 Loading more articles...');
  
  const newsGrid = document.querySelector('.news-grid');
  if (newsGrid) {
    // Show loading state
    const loadingCard = document.createElement('div');
    loadingCard.className = 'news-card loading';
    loadingCard.innerHTML = `
      <div class="loading">
        <div class="loading-spinner"></div>
        <p>Cargando más noticias...</p>
      </div>
    `;
    newsGrid.appendChild(loadingCard);
    
    // Simulate API call
    setTimeout(() => {
      loadingCard.remove();
      console.log('✅ More articles loaded');
    }, 1500);
  }
}

/**
 * Share article to social media
 */
function shareArticle(title, url) {
  if (navigator.share) {
    navigator.share({
      title: title,
      url: url
    }).then(() => {
      console.log('✅ Shared successfully');
    }).catch((error) => {
      console.log('❌ Share failed:', error);
    });
  } else {
    // Fallback: copy to clipboard
    navigator.clipboard.writeText(url).then(() => {
      console.log('✅ URL copied to clipboard');
      alert('Enlace copiado al portapapeles');
    });
  }
}

/**
 * Filter news by category
 */
function filterNewsByCategory(category) {
  const newsCards = document.querySelectorAll('.news-card');
  
  newsCards.forEach(card => {
    const cardCategory = card.querySelector('.news-card-category').textContent.toLowerCase();
    
    if (category === 'all' || cardCategory.includes(category.toLowerCase())) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

/**
 * Search news articles
 */
function searchNews(query) {
  const newsCards = document.querySelectorAll('.news-card');
  const searchTerm = query.toLowerCase();
  
  newsCards.forEach(card => {
    const title = card.querySelector('h3').textContent.toLowerCase();
    const summary = card.querySelector('p').textContent.toLowerCase();
    
    if (title.includes(searchTerm) || summary.includes(searchTerm)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

/**
 * Initialize tooltips for player info
 */
function initPlayerTooltips() {
  const playerNames = document.querySelectorAll('.team-name, .pair-info strong');
  
  playerNames.forEach(name => {
    name.addEventListener('mouseenter', function() {
      // In production, this would show a tooltip with player stats
      console.log('👤 Player hover:', this.textContent);
    });
  });
}

// Expose functions globally for inline handlers
window.scrollToSection = scrollToSection;
window.loadMoreNews = loadMoreNews;
window.shareArticle = shareArticle;
window.filterNewsByCategory = filterNewsByCategory;
window.searchNews = searchNews;

/**
 * Performance monitoring
 */
if (window.performance) {
  window.addEventListener('load', () => {
    const timing = window.performance.timing;
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    console.log(`⚡ Page load time: ${loadTime}ms`);
  });
}

/**
 * Error handling for images
 */
document.addEventListener('error', function(e) {
  if (e.target.tagName === 'IMG') {
    // Replace broken images with placeholder
    const placeholder = `https://placehold.co/600x400/0066cc/ffffff?text=Imagen+no+disponible`;
    if (e.target.src !== placeholder) {
      e.target.src = placeholder;
      console.log('🖼️ Image replaced with placeholder:', e.target.alt);
    }
  }
}, true);

console.log('✅ Padel News Pro initialized');
