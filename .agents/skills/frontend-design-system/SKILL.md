---
name: frontend-design-system
description: Design system guidelines, layout rules, token usage, component conventions, and Chart.js standards for the Smart Wealth Tracker web application.
---

# Frontend Design System & Component Guidelines

## When to Use This Skill
Activate this skill whenever writing or modifying HTML templates, CSS styles, JavaScript widgets, or Chart.js visualizations.

---

## 1. Architecture & Template Inheritance
- Every internal authenticated template must extend `tracker/base.html` using:
  ```html
  {% extends 'tracker/base.html' %}
  {% block title %}Page Title - Smart Wealth Tracker{% endblock %}
  {% block content %} ... {% endblock %}
  ```
- Public unauthenticated pages (Landing, Login, Signup) use the dedicated dual-panel layout styles while maintaining color token consistency.

---

## 2. Design Tokens Usage
Always use CSS variables defined in `static/css/style.css`:
- **Primary Indigo:** `var(--primary)` (`#4f46e5`), `var(--primary-light)` (`#eef2ff`)
- **Success Emerald (Income / On Track):** `var(--success)` (`#10b981`), `var(--success-light)` (`#ecfdf5`)
- **Danger Red (Expenses / Exceeded):** `var(--danger)` (`#ef4444`), `var(--danger-light)` (`#fef2f2`)
- **Warning Amber (80% Budget Alert):** `var(--warning)` (`#f59e0b`)
- **AI Purple:** `var(--purple)` (`#8b5cf6`), `var(--purple-light)` (`#f5f3ff`)
- **Neutral Backgrounds:** `var(--bg-body)` (`#f8fafc`), `var(--bg-card)` (`#ffffff`)
- **Borders & Shadows:** `var(--border-color)` (`#e2e8f0`), `var(--shadow-sm)`, `var(--shadow-md)`

---

## 3. Standard Component Patterns

### KPI Stat Cards
```html
<div class="stat-card stat-balance">
    <span class="stat-label">Net Balance</span>
    <div class="stat-value">₹{{ balance }}</div>
    <div class="stat-meta"><span>Current available liquidity</span></div>
</div>
```

### Modern Tables
```html
<div class="card">
    <div class="table-responsive">
        <table class="data-table">
            <thead> ... </thead>
            <tbody> ... </tbody>
        </table>
    </div>
</div>
```

### Action Buttons
- Primary CTA: `<button type="submit" class="btn btn-primary">Save Changes &rarr;</button>`
- Secondary: `<a href="..." class="btn btn-secondary">Cancel</a>`
- Danger: `<a href="..." class="btn btn-danger btn-sm" onclick="return confirm(...)">Delete</a>`

---

## 4. Chart.js Styling Standards
- **Font:** Inherits application system font (`Inter`).
- **Donut Cutout:** Always `cutout: '60%'`.
- **Bar Radius:** Always `borderRadius: 6`.
- **Palette Order:** Indigo (`#4f46e5`), Emerald (`#10b981`), Amber (`#f59e0b`), Rose (`#ef4444`), Violet (`#8b5cf6`), Cyan (`#06b6d4`).
