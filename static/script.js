// Cart functionality
$(document).ready(function() {
    // Update cart count in navbar
    function updateCartCount() {
        if (window.location.pathname !== '/cart') {
            $.get('/api/cart_count', function(data) {
                const badge = $('.navbar .badge');
                if (data.count > 0) {
                    badge.text(data.count).show();
                } else {
                    badge.hide();
                }
            }).fail(function() {
                console.log('Failed to fetch cart count');
            });
        }
    }

    // Initialize cart count on page load
    updateCartCount();

    // Auto-update cart when quantity changes
    $('input[name="quantity"]').on('change', function() {
        const form = $(this).closest('form');
        const submitBtn = form.find('button[type="submit"]');
        
        // Show loading state
        submitBtn.html('<i class="fas fa-spinner fa-spin"></i>');
        submitBtn.prop('disabled', true);

        // Submit form
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                // Reload page to reflect changes
                window.location.reload();
            },
            error: function() {
                alert('Error updating cart. Please try again.');
                submitBtn.html('<i class="fas fa-sync-alt"></i>');
                submitBtn.prop('disabled', false);
            }
        });
    });

    // Add to cart with AJAX
    $('.add-to-cart-btn').on('click', function(e) {
        e.preventDefault();
        const btn = $(this);
        const originalText = btn.html();
        const productId = btn.data('product-id');
        
        // Show loading state
        btn.html('<i class="fas fa-spinner fa-spin"></i> Adding...');
        btn.prop('disabled', true);

        $.get(`/add_to_cart/${productId}`, function(response) {
            // Restore button state
            btn.html(originalText);
            btn.prop('disabled', false);
            
            // Show success message
            showFlashMessage('Product added to cart!', 'success');
            
            // Update cart count
            updateCartCount();
            
        }).fail(function() {
            btn.html(originalText);
            btn.prop('disabled', false);
            showFlashMessage('Error adding product to cart', 'error');
        });
    });

    // Remove from cart with confirmation
    $('.remove-from-cart').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            window.location.href = url;
        }
    });

    // Flash message function
    function showFlashMessage(message, type) {
        const alertClass = type === 'error' ? 'alert-danger' : 'alert-success';
        const flashHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show flash-message-auto">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        $('.container').prepend(flashHtml);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            $('.flash-message-auto').alert('close');
        }, 3000);
    }

    // Product search enhancement
    $('#searchInput').on('input', function() {
        const query = $(this).val();
        if (query.length > 2) {
            // You can add live search functionality here
            console.log('Search query:', query);
        }
    });

    // Price filter functionality
    $('.price-filter').on('change', function() {
        const priceRange = $(this).val();
        // Implement price filtering logic
        filterProductsByPrice(priceRange);
    });

    // Category filter with AJAX
    $('.category-filter').on('click', function(e) {
        e.preventDefault();
        const categoryId = $(this).data('category-id');
        
        $('.category-filter').removeClass('active');
        $(this).addClass('active');
        
        // Show loading state
        $('#products-container').html('<div class="text-center py-5"><i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading products...</p></div>');
        
        // Load category products
        $.get(`/category/${categoryId}`, function(data) {
            const productsHtml = $(data).find('#products-container').html();
            $('#products-container').html(productsHtml);
        });
    });

    // Smooth scroll to top
    $('.scroll-to-top').on('click', function(e) {
        e.preventDefault();
        $('html, body').animate({ scrollTop: 0 }, 500);
    });

    // Payment method selection effects
    $('#payment_method').on('change', function() {
        const method = $(this).val();
        $('.payment-method-info').hide();
        $(`.payment-info-${method}`).show();
    });

    // Quantity input validation
    $('input[type="number"]').on('input', function() {
        const value = parseInt($(this).val());
        const max = parseInt($(this).attr('max')) || 10;
        const min = parseInt($(this).attr('min')) || 1;
        
        if (value > max) {
            $(this).val(max);
        } else if (value < min) {
            $(this).val(min);
        }
    });

    // Add to wishlist functionality
    $('.wishlist-btn').on('click', function(e) {
        e.preventDefault();
        const btn = $(this);
        const productId = btn.data('product-id');
        
        btn.toggleClass('active');
        if (btn.hasClass('active')) {
            btn.html('<i class="fas fa-heart text-danger"></i>');
            showFlashMessage('Added to wishlist!', 'success');
        } else {
            btn.html('<i class="far fa-heart"></i>');
            showFlashMessage('Removed from wishlist', 'info');
        }
        
        // Here you would typically make an AJAX call to update wishlist
        // $.post('/wishlist/add', { product_id: productId });
    });

    // Product image zoom on hover
    $('.product-image').on('mouseenter', function() {
        $(this).css('transform', 'scale(1.05)');
    }).on('mouseleave', function() {
        $(this).css('transform', 'scale(1)');
    });

    // Stock availability check
    function checkStock() {
        $('.stock-badge').each(function() {
            const stock = parseInt($(this).data('stock'));
            if (stock < 5) {
                $(this).removeClass('bg-success').addClass('bg-warning').text('Low Stock');
            } else if (stock === 0) {
                $(this).removeClass('bg-success').addClass('bg-danger').text('Out of Stock');
                $(this).closest('.card').find('.add-to-cart-btn').prop('disabled', true).text('Out of Stock');
            }
        });
    }

    // Initialize stock check
    checkStock();

    // Order status tracking
    $('.track-order').on('click', function() {
        const orderId = $(this).data('order-id');
        // Implement order tracking modal or page
        alert(`Tracking order #${orderId}`);
    });

    // Address form validation
    $('#checkout-form').on('submit', function(e) {
        const pincode = $('#pincode').val();
        if (pincode.length !== 6 || isNaN(pincode)) {
            e.preventDefault();
            showFlashMessage('Please enter a valid 6-digit PIN code', 'error');
            $('#pincode').focus();
        }
    });

    // Real-time shipping cost calculation
    function calculateShipping() {
        const subtotal = parseFloat($('#subtotal').data('amount')) || 0;
        let shipping = subtotal >= 499 ? 0 : 50;
        
        $('#shipping-cost').text(shipping === 0 ? 'FREE' : `₹${shipping}`);
        $('#total-amount').text(`₹${(subtotal + shipping).toFixed(2)}`);
        
        // Show free shipping message
        if (subtotal < 499) {
            const needed = 499 - subtotal;
            $('#free-shipping-message').html(`Add <strong>₹${needed.toFixed(2)}</strong> more for free shipping!`).show();
        } else {
            $('#free-shipping-message').hide();
        }
    }

    // Initialize shipping calculation
    calculateShipping();

    // Newsletter subscription
    $('#newsletter-form').on('submit', function(e) {
        e.preventDefault();
        const email = $('#newsletter-email').val();
        
        $.post('/newsletter/subscribe', { email: email }, function(response) {
            showFlashMessage('Thank you for subscribing!', 'success');
            $('#newsletter-email').val('');
        }).fail(function() {
            showFlashMessage('Subscription failed. Please try again.', 'error');
        });
    });

    // Product quick view
    $('.quick-view-btn').on('click', function() {
        const productId = $(this).data('product-id');
        // Implement quick view modal
        console.log('Quick view product:', productId);
    });

    // Back to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn();
        } else {
            $('.back-to-top').fadeOut();
        }
    });

    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
});

// Utility functions
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

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