# 05. UI Design System: Smart Wealth Tracker and Budget Planner

This document establishes the UI design language, tokens, component library, typography, layout rules, and chart aesthetics across the entire application.

---

## 1. Design Principles & Aesthetic Direction
1. **Calm, High-Trust Fintech Aesthetic:** Clean whites, soft slate backgrounds, and purposeful semantic accents (indigo for balance, emerald for income, rose for expenses, violet for AI).
2. **Card-Based Visual Hierarchy:** Information is grouped in elevated cards with subtle border outlines and soft ambient shadows.
3. **Responsive by Default:** Fluid layouts adapting seamlessly from mobile viewports (360px) to widescreen desktop monitors (1440px+).
4. **Accessible & High-Contrast:** Compliant with WCAG AA contrast standards; legible font sizes and unmistakable interactive focus states.

---

## 2. Design Tokens (CSS Custom Properties)

```css
:root {
  /* Brand Primaries */
  --primary: #4f46e5;           /* Indigo-600 */
  --primary-hover: #4338ca;     /* Indigo-700 */
  --primary-light: #eef2ff;     /* Indigo-50 */
  --primary-border: #c7d2fe;    /* Indigo-200 */

  /* Semantic Status Colors */
  --success: #10b981;           /* Emerald-500 (Income / On Track) */
  --success-dark: #059669;      /* Emerald-600 */
  --success-light: #ecfdf5;     /* Emerald-50 */
  --success-border: #a7f3d0;    /* Emerald-200 */

  --danger: #ef4444;            /* Red-500 (Expense / Exceeded) */
  --danger-dark: #dc2626;       /* Red-600 */
  --danger-light: #fef2f2;      /* Red-50 */
  --danger-border: #fecaca;     /* Red-200 */

  --warning: #f59e0b;           /* Amber-500 (Budget warning at 80%) */
  --warning-light: #fffbeb;     /* Amber-50 */
  --warning-border: #fde68a;    /* Amber-200 */

  --purple: #8b5cf6;            /* Violet-500 (AI & ML Insights) */
  --purple-light: #f5f3ff;      /* Violet-50 */
  --purple-border: #ddd6fe;     /* Violet-200 */

  /* Neutrals & Surfaces */
  --bg-body: #f8fafc;           /* Slate-50 */
  --bg-card: #ffffff;           /* White */
  --bg-input: #ffffff;
  --border-color: #e2e8f0;      /* Slate-200 */

  /* Typography */
  --text-main: #0f172a;         /* Slate-900 */
  --text-muted: #64748b;        /* Slate-500 */
  --text-light: #94a3b8;        /* Slate-400 */

  /* Shadows */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.08);

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

---

## 3. Dark Mode Palette Tokens (When Enabled)
```css
[data-theme="dark"] {
  --bg-body: #0b1120;           /* Deep Navy / Slate-950 */
  --bg-card: #151f32;           /* Dark Card Surface */
  --bg-input: #1e293b;          /* Slate-800 */
  --border-color: #27354f;      /* Slate-700 */
  --text-main: #f8fafc;         /* Slate-50 */
  --text-muted: #94a3b8;        /* Slate-400 */
  --text-light: #64748b;        /* Slate-500 */
}
```

---

## 4. Typography Scale
- **Font Family:** `-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif`.
- **H1 (Page Headers):** `1.65rem` (`26px`), Weight: 700, Letter-spacing: `-0.02em`.
- **H2 (Section Titles):** `1.25rem` (`20px`), Weight: 700.
- **H3 (Card Titles):** `1.15rem` (`18px`), Weight: 600.
- **KPI Large Numbers:** `1.85rem` to `2.25rem`, Weight: 800.
- **Body Text:** `0.92rem` to `0.95rem` (`15px`), Line height: `1.5`.
- **Microcopy & Captions:** `0.80rem` to `0.85rem` (`13px`).

---

## 5. Reusable Component Rules

### 5.1 KPI Stat Cards
- Must have a colored 4px top accent strip (`::before` pseudoclass).
- Must show label in uppercase tracking (`font-size: 0.85rem; letter-spacing: 0.05em;`).
- Currency amount rendered in large bold text with Indian Rupee prefix (₹).
- Subtitle provides explanatory context (e.g., *"Cumulative recorded spending"*).

### 5.2 Data Tables (`.data-table`)
- Table headers use subtle slate background `#f8fafc`, uppercase small caps text, and clean bottom border.
- Table rows feature subtle hover background transition (`#f8fafc`).
- Actions (Edit, Delete) positioned right-aligned in compact buttons (`.btn-sm`).

### 5.3 Badges & Pills (`.badge`)
- Rounded pills (`border-radius: 9999px`).
- `.badge-income`: Soft emerald background, dark emerald text.
- `.badge-expense`: Soft rose background, dark rose text.
- `.badge-ontrack`: Green outline pill indicating budget/goal health.
- `.badge-exceeded`: Crimson pill with warning icon for budget overruns.

### 5.4 Form Controls & Buttons
- Inputs have `padding: 11px 14px;`, border `1px solid #cbd5e1;`, and border-radius `6px`.
- On focus: Indigo border with `box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15)`.
- `.btn-primary`: Vibrant gradient `linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)` with subtle lift animation on hover (`transform: translateY(-1px)`).

---

## 6. Chart.js Visual Guidelines
- **Font:** Inherits application system font (`Inter`).
- **Donut Chart (Category Breakdown):** Cutout set to `60%` for modern ring look; borders white with width `2px`.
- **Bar Chart (Monthly Cash Flow):** Border radius on bars `6px`; grid lines muted (`#f1f5f9`); Y-axis labels prefixed with ₹ currency sign.
- **Color Palette Sequence:**
  1. Indigo: `#4f46e5`
  2. Emerald: `#10b981`
  3. Amber: `#f59e0b`
  4. Rose: `#ef4444`
  5. Violet: `#8b5cf6`
  6. Cyan: `#06b6d4`
  7. Pink: `#ec4899`
