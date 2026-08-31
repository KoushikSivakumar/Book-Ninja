/**
 * Book Ninja - Frontend JavaScript
 * All vanilla JavaScript for UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(20px)';
            setTimeout(function() {
                if (msg.parentElement) {
                    msg.remove();
                }
            }, 300);
        }, 5000);
    });

    // Close flash message on click of close button
    document.querySelectorAll('.flash-close').forEach(function(btn) {
        btn.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });

    // Book card hover effect - subtle tilt (desktop only)
    if (window.innerWidth > 768) {
        document.querySelectorAll('.book-card').forEach(function(card) {
            card.addEventListener('mouseenter', function() {
                this.style.transition = 'transform 0.25s ease, box-shadow 0.25s ease';
            });
        });
    }

    // Quantity input validation
    document.querySelectorAll('.qty-input').forEach(function(input) {
        input.addEventListener('change', function() {
            let val = parseInt(this.value) || 1;
            const min = parseInt(this.getAttribute('min')) || 1;
            const max = parseInt(this.getAttribute('max')) || 999;
            if (val < min) this.value = min;
            if (val > max) this.value = max;
        });
    });

    // Mobile nav collapse on link click
    document.querySelectorAll('.navbar-nav .nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            const navbar = document.querySelector('.navbar-collapse');
            if (navbar && navbar.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbar);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
    });

    // Search input enhancement - clear button
    document.querySelectorAll('.catalogue-search .search-input').forEach(function(input) {
        input.addEventListener('search', function() {
            // Native search clear triggers this
        });
    });

    // Newsletter form (handled in index.html)
    // Additional newsletter form handling for any other instances
    document.querySelectorAll('.newsletter-form:not(#newsletterForm)').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const input = this.querySelector('input[type="email"]');
            const messageEl = this.querySelector('.newsletter-message') || 
                             (() => {
                                const el = document.createElement('div');
                                el.className = 'newsletter-message';
                                this.appendChild(el);
                                return el;
                             })();
            
            if (input && input.value.includes('@')) {
                messageEl.innerHTML = '✅ Thank you for subscribing!';
                messageEl.className = 'newsletter-message success';
                input.value = '';
                setTimeout(() => {
                    messageEl.innerHTML = '';
                    messageEl.className = 'newsletter-message';
                }, 4000);
            } else {
                messageEl.innerHTML = '⚠️ Please enter a valid email address.';
                messageEl.className = 'newsletter-message error';
            }
        });
    });

    // Admin delete confirmation
    document.querySelectorAll('.admin-table .action-delete').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Image fallback for book covers
    document.querySelectorAll('.book-card-image img, .cart-item-cover img, .book-detail-cover img').forEach(function(img) {
        img.addEventListener('error', function() {
            this.src = '/static/images/books/placeholder.jpg';
        });
    });

    // Wishlist button visual feedback (handled in book_detail.html for specific)
    // General wishlist toggle for any other instances
    document.querySelectorAll('.btn-wishlist[data-book-id]').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            // If not handled by inline onclick, handle here
            const bookId = this.getAttribute('data-book-id');
            if (bookId && !this.getAttribute('onclick')) {
                e.preventDefault();
                fetch(`/wishlist/toggle/${bookId}`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    const icon = this.querySelector('i');
                    const text = this.querySelector('span');
                    if (data.wishlisted) {
                        icon.className = 'bi bi-heart-fill';
                        if (text) text.textContent = 'Remove from Wishlist';
                    } else {
                        icon.className = 'bi bi-heart';
                        if (text) text.textContent = 'Add to Wishlist';
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });

    // Smooth scroll for category bar scroll buttons
    // Handled in index.html

    console.log('📚 Book Ninja initialized.');
});