/**
 * SnapTrace Website JavaScript
 * Handles image modals, smooth scrolling, and interactive elements
 */

(function() {
    'use strict';

    // DOM Elements
    let modal = null;
    let modalImage = null;
    let modalCaption = null;
    let closeBtn = null;

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeModal();
        initializeSmoothScrolling();
        initializeScreenshotGallery();
        initializeHeader();
    });

    /**
     * Initialize the image modal functionality
     */
    // function initializeModal() {
    //     modal = document.getElementById('imageModal');
    //     modalImage = document.getElementById('modalImage');
    //     modalCaption = document.querySelector('.modal-caption');
    //     closeBtn = document.querySelector('.modal-close');

    //     if (!modal || !modalImage || !closeBtn) {
    //         console.warn('Modal elements not found');
    //         return;
    //     }

    //     // Close modal when clicking the X
    //     closeBtn.addEventListener('click', closeModal);

    //     // Close modal when clicking outside the image
    //     modal.addEventListener('click', function(e) {
    //         if (e.target === modal) {
    //             closeModal();
    //         }
    //     });

    //     // Close modal with Escape key
    //     document.addEventListener('keydown', function(e) {
    //         if (e.key === 'Escape' && modal.style.display === 'block') {
    //             closeModal();
    //         }
    //     });
    // }

    /**
     * Initialize smooth scrolling for navigation links
     */
    function initializeSmoothScrolling() {
        const navLinks = document.querySelectorAll('a[href^="#"]');
        
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const headerHeight = 80; // Account for fixed header
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    /**
     * Initialize screenshot gallery with modal functionality
     */
    function initializeScreenshotGallery() {
        const screenshotImages = document.querySelectorAll('.screenshot-img, .hero-image');
        
        screenshotImages.forEach(img => {
            img.style.cursor = 'pointer';
            img.addEventListener('click', function() {
                openModal(this);
            });

            // Add hover effect
            const container = img.closest('.screenshot-container');
            if (container) {
                container.addEventListener('mouseenter', function() {
                    const overlay = this.querySelector('.screenshot-overlay');
                    if (overlay) {
                        overlay.style.opacity = '1';
                    }
                });

                container.addEventListener('mouseleave', function() {
                    const overlay = this.querySelector('.screenshot-overlay');
                    if (overlay) {
                        overlay.style.opacity = '0';
                    }
                });
            }
        });
    }

    /**
     * Initialize header scroll behavior
     */
    function initializeHeader() {
        const header = document.querySelector('.header');
        if (!header) return;

        let lastScrollY = window.scrollY;

        window.addEventListener('scroll', function() {
            const currentScrollY = window.scrollY;
            
            // Add/remove scrolled class for styling
            if (currentScrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }

            lastScrollY = currentScrollY;
        });
    }

    /**
     * Open the image modal
     * @param {HTMLImageElement} img - The image to display
     */
    function openModal(img) {
        if (!modal || !modalImage) return;

        modalImage.src = img.src;
        modalImage.alt = img.alt;
        
        if (modalCaption) {
            modalCaption.textContent = img.alt;
        }
        
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    /**
     * Close the image modal
     */
    function closeModal() {
        if (!modal) return;
        
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling
    }

    /**
     * Download button functionality
     */
    function initializeDownloadButtons() {
        const downloadButtons = document.querySelectorAll('.btn[href*="releases"]');
        
        downloadButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Track download clicks if analytics are implemented
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'download', {
                        'event_category': 'engagement',
                        'event_label': 'SnapTrace Download'
                    });
                }
            });
        });
    }

    /**
     * Initialize animations on scroll (optional enhancement)
     */
    function initializeScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements that should animate in
        const animateElements = document.querySelectorAll('.feature-item, .screenshot-item, .doc-item');
        animateElements.forEach(el => {
            observer.observe(el);
        });
    }

    // Initialize additional features
    document.addEventListener('DOMContentLoaded', function() {
        initializeDownloadButtons();
        
        // Only initialize scroll animations if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            initializeScrollAnimations();
        }
    });

    // Expose some functions globally if needed
    window.SnapTraceWebsite = {
        openModal: openModal,
        closeModal: closeModal
    };

})();
