(function() {
    'use strict';

    // Get elements
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('ratingInput');
    const ratingValue = document.getElementById('ratingValue');
    const form = document.getElementById('movieForm');
    const starContainer = document.getElementById('starContainer');

    // Validate all required elements exist
    if (!stars.length) {
        console.error('❌ Rating system: No star elements found');
        return;
    }
    if (!ratingInput) {
        console.error('❌ Rating system: ratingInput element not found');
        return;
    }
    if (!ratingValue) {
        console.error('❌ Rating system: ratingValue element not found');
        return;
    }
    if (!form) {
        console.error('❌ Rating system: movieForm not found');
        return;
    }
    if (!starContainer) {
        console.error('❌ Rating system: starContainer not found');
        return;
    }

    // Initialize with current rating
    let currentRating = parseInt(ratingInput.value) || 0;

    console.log('🎬 Movie Rating Script Loaded');
    console.log('📊 Initial rating:', currentRating);
    console.log('⭐ Found', stars.length, 'stars');

    /**
     * Update star display and input value
     * @param {number} rating - Rating value (0-5)
     */
    function updateStars(rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('filled');
                star.classList.remove('hover');
            } else {
                star.classList.remove('filled', 'hover');
            }
        });

        // Update text display and hidden input
        ratingValue.textContent = rating;
        ratingInput.value = rating;

        console.log('⭐ Updated to:', rating);
    }

    /**
     * Handle hover effect over stars
     * @param {number} hoverValue - Value being hovered over
     */
    function handleHover(hoverValue) {
        stars.forEach((star, index) => {
            if (index < hoverValue) {
                star.classList.add('hover');
            } else {
                star.classList.remove('hover');
            }
        });
    }

    // Initialize display with current rating
    updateStars(currentRating);

    // Add click handlers to each star
    stars.forEach((star, index) => {
        star.addEventListener('click', function() {
            const value = parseInt(this.getAttribute('data-value'));

            console.log('🖱️ Clicked star:', value);

            // Toggle: clicking same rating sets to 0 (unrate)
            if (value === currentRating) {
                currentRating = 0;
            } else {
                currentRating = value;
            }

            updateStars(currentRating);
        });

        // Hover effect - show preview of rating
        star.addEventListener('mouseenter', function() {
            const hoverValue = parseInt(this.getAttribute('data-value'));
            handleHover(hoverValue);
        });
    });

    // Reset hover effect when mouse leaves container
    starContainer.addEventListener('mouseleave', function() {
        updateStars(currentRating);
    });

    // Form submit handler with validation
    form.addEventListener('submit', function(e) {
        console.log('📤 SUBMITTING FORM');
        console.log('   Rating value:', ratingInput.value);
        console.log('   Status:', document.getElementById('status').value);
        console.log('   Plot length:', document.getElementById('plot').value.length);

        // Optional: Add confirmation dialog
        // Uncomment the lines below if you want a confirmation prompt
        /*
        const confirmation = confirm(
            `Save changes with rating: ${ratingInput.value}/5?`
        );
        if (!confirmation) {
            e.preventDefault();
        }
        */
    });

    console.log('✅ Rating system initialized successfully');

})();