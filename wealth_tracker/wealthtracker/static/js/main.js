/**
 * Smart Wealth Tracker - Main Frontend JavaScript (static/js/main.js)
 * Manages theme switching (dark/light), sidebar toggling, tooltips, and interactive widgets.
 */

(function () {
  'use strict';

  // 1. Theme Switcher (Dark / Light Mode)
  const THEME_STORAGE_KEY = 'wealth_theme';

  function getPreferredTheme() {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);

    // Update icon on all theme toggle buttons
    const toggleButtons = document.querySelectorAll('.theme-toggle-btn');
    toggleButtons.forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'bi bi-sun-fill text-warning';
          btn.setAttribute('title', 'Switch to Light Mode');
        } else {
          icon.className = 'bi bi-moon-stars-fill text-secondary';
          btn.setAttribute('title', 'Switch to Dark Mode');
        }
      }
    });

    // Notify any active charts to update styling
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }

  // Initial Theme Application before DOM load to avoid flash
  applyTheme(getPreferredTheme());

  document.addEventListener('DOMContentLoaded', function () {
    // Re-sync theme button icons after DOM is ready
    applyTheme(getPreferredTheme());

    // Event listeners for theme toggle buttons
    const toggleButtons = document.querySelectorAll('.theme-toggle-btn');
    toggleButtons.forEach(btn => {
      btn.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(nextTheme);
      });
    });

    // 2. Mobile Sidebar Toggle
    const sidebar = document.getElementById('appSidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    function toggleSidebar() {
      if (sidebar) {
        sidebar.classList.toggle('show');
        if (sidebarBackdrop) {
          sidebarBackdrop.classList.toggle('show');
        }
      }
    }

    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', toggleSidebar);
    }
    if (sidebarBackdrop) {
      sidebarBackdrop.addEventListener('click', toggleSidebar);
    }

    // Close sidebar when pressing ESC
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar && sidebar.classList.contains('show')) {
        toggleSidebar();
      }
    });

    // 3. Initialize Bootstrap Tooltips & Popovers
    if (typeof bootstrap !== 'undefined') {
      const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    }

    // 4. Auto-Dismiss Flash Alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert-dismiss-auto');
    autoAlerts.forEach(alert => {
      setTimeout(() => {
        if (typeof bootstrap !== 'undefined') {
          const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
          if (bsAlert) bsAlert.close();
        } else {
          alert.style.transition = 'opacity 0.5s ease';
          alert.style.opacity = '0';
          setTimeout(() => alert.remove(), 500);
        }
      }, 5000);
    });

    // 5. Global Quick-Add Modal AI Suggestion Handler
    const modalDescInput = document.getElementById('modal_id_description');
    const modalCatSelect = document.getElementById('modal_id_category');
    const modalAiBtn = document.getElementById('modalAiPredictBtn');
    const modalAiResult = document.getElementById('modalAiResult');

    if (modalAiBtn && modalDescInput) {
      modalAiBtn.addEventListener('click', function () {
        const desc = modalDescInput.value.trim();
        if (!desc) {
          if (modalAiResult) {
            modalAiResult.textContent = 'Please type a description first!';
            modalAiResult.className = 'text-danger small fw-bold';
          }
          return;
        }

        if (modalAiResult) {
          modalAiResult.textContent = 'AI predicting...';
          modalAiResult.className = 'text-primary small fw-semibold';
        }

        fetch(`/api/predict-category/?desc=${encodeURIComponent(desc)}`)
          .then(res => res.json())
          .then(data => {
            if (data.predicted_category) {
              if (modalAiResult) {
                modalAiResult.textContent = `Predicted: ${data.predicted_category} (${data.confidence}% conf)`;
                modalAiResult.className = 'text-success small fw-bold';
              }
              if (modalCatSelect && data.category_id) {
                modalCatSelect.value = data.category_id;
              } else if (modalCatSelect) {
                const target = data.predicted_category.toLowerCase();
                for (let i = 0; i < modalCatSelect.options.length; i++) {
                  if (modalCatSelect.options[i].text.toLowerCase() === target) {
                    modalCatSelect.selectedIndex = i;
                    break;
                  }
                }
              }
            }
          })
          .catch(() => {
            if (modalAiResult) {
              modalAiResult.textContent = 'AI service unavailable.';
              modalAiResult.className = 'text-danger small';
            }
          });
      });
    }
  });

})();
