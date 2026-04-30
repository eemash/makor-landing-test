/* ============================================
   MÁKOR COFFEE — Interactions
   ============================================ */

(function () {
  'use strict';

  // --- Scroll-based nav styling ---
  var nav = document.getElementById('nav');

  function updateNav() {
    if (window.scrollY > 60) {
      nav.classList.add('nav--scrolled');
    } else {
      nav.classList.remove('nav--scrolled');
    }
  }

  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();

  // --- Mobile menu toggle ---
  var mobileToggle = document.getElementById('mobileToggle');
  var mobileMenu = document.getElementById('mobileMenu');
  var menuOpen = false;

  mobileToggle.addEventListener('click', function () {
    menuOpen = !menuOpen;
    mobileMenu.classList.toggle('active', menuOpen);
    document.body.style.overflow = menuOpen ? 'hidden' : '';

    var spans = mobileToggle.querySelectorAll('span');
    if (menuOpen) {
      spans[0].style.transform = 'rotate(45deg) translate(3px, 3px)';
      spans[1].style.transform = 'rotate(-45deg) translate(1px, -1px)';
    } else {
      spans[0].style.transform = '';
      spans[1].style.transform = '';
    }
  });

  // Close mobile menu on link click
  var mobileLinks = mobileMenu.querySelectorAll('a');
  for (var i = 0; i < mobileLinks.length; i++) {
    mobileLinks[i].addEventListener('click', function () {
      menuOpen = false;
      mobileMenu.classList.remove('active');
      document.body.style.overflow = '';
      var spans = mobileToggle.querySelectorAll('span');
      spans[0].style.transform = '';
      spans[1].style.transform = '';
    });
  }

  // --- Intersection Observer for scroll animations ---
  var animatedElements = document.querySelectorAll('[data-animate]');

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
        rootMargin: '0px 0px -40px 0px',
      }
    );

    animatedElements.forEach(function (el, index) {
      el.style.transitionDelay = (index % 3) * 0.12 + 's';
      observer.observe(el);
    });
  } else {
    // Fallback for older browsers
    animatedElements.forEach(function (el) {
      el.classList.add('visible');
    });
  }

  // --- Smooth anchor scrolling with offset ---
  var anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (href === '#') return;

      var target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        var offset = nav.offsetHeight + 20;
        var top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });
})();
