(function() {
            'use strict';

            // Get elements
            const stars = document.querySelectorAll('.star');
            const ratingInput = document.getElementById('ratingInput');
            const ratingValue = document.getElementById('ratingValue');
            const debugValue = document.getElementById('debugValue');
            const form = document.getElementById('movieForm');

            // Initialize with current rating
            let currentRating = parseInt(ratingInput.value) || 0;

            console.log('🎬 Movie Rating Script Loaded');
            console.log('📊 Initial rating:', currentRating);

            // Function to update star display
            function updateStars(rating) {
                stars.forEach((star, index) => {
                    if (index < rating) {
                        star.classList.add('filled');
                        star.classList.remove('hover');
                    } else {
                        star.classList.remove('filled');
                        star.classList.remove('hover');
                    }
                });

                // Update text displays
                ratingValue.textContent = rating;
                ratingInput.value = rating;
                debugValue.textContent = rating;

                console.log('⭐ Updated to:', rating);
            }

            // Initialize display
            updateStars(currentRating);

            // Click handler
            stars.forEach(star => {
                star.addEventListener('click', function() {
                    const value = parseInt(this.getAttribute('data-value'));

                    // Toggle: clicking same rating sets to 0
                    if (value === currentRating) {
                        currentRating = 0;
                    } else {
                        currentRating = value;
                    }

                    updateStars(currentRating);
                });

                // Hover effect
                star.addEventListener('mouseenter', function() {
                    const hoverValue = parseInt(this.getAttribute('data-value'));
                    stars.forEach((s, index) => {
                        if (index < hoverValue) {
                            s.classList.add('hover');
                        } else {
                            s.classList.remove('hover');
                        }
                    });
                });
            });

            // Reset hover on mouse leave
            document.getElementById('starContainer').addEventListener('mouseleave', function() {
                updateStars(currentRating);
            });

            // Form submit handler (for debugging)
            form.addEventListener('submit', function(e) {
                console.log('📤 SUBMITTING FORM');
                console.log('   Rating value:', ratingInput.value);
                console.log('   Status:', document.getElementById('status').value);
                console.log('   Plot length:', document.getElementById('plot').value.length);

                // Show alert to confirm
                const confirmation = confirm(
                    `Save changes with rating: ${ratingInput.value}/5?`
                );

                if (!confirmation) {
                    e.preventDefault();
                }
            });

        })();