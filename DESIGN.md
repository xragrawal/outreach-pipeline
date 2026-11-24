---
name: Antseed Outreach Pipeline
description: An auditable company-to-outreach workspace built around a visible five-stage narrowing flow.
colors:
  primary: "#4f7a24"
  primary-hover: "#436a1e"
  acid-highlight: "#c8f53c"
  selection-ink: "#0a1a12"
  day-title: "#1c1c1c"
  day-title-muted: "#595959"
  day-text: "#30382c"
  day-body: "#56656f"
  day-small: "#66746b"
  day-grey: "#929292"
  day-page: "#fcfcfc"
  day-rail: "#ffffff"
  day-dot: "#e2e2e2"
  day-dot-off: "#e6eadc"
  day-tile: "rgba(214, 219, 211, 0.2)"
  day-line: "rgba(64, 76, 66, 0.1)"
  day-wash: "#f6f3ea"
  day-error: "#a42f28"
  day-warning: "#725800"
  night-primary: "#98c463"
  night-primary-hover: "#5b8a2b"
  night-text: "#eceee9"
  night-muted: "#9ba49e"
  night-page: "#0f1312"
  night-rail: "#181d1b"
  night-dot: "#3d4340"
  night-dot-off: "#29302c"
  night-tile: "rgba(255, 255, 255, 0.06)"
  night-line: "rgba(255, 255, 255, 0.1)"
  night-wash: "#39403d"
  night-error: "#ff8f87"
  night-warning: "#ffd166"
  white: "#ffffff"
typography:
  display:
    fontFamily: '"Geist Pixel Var", "Geist", sans-serif'
    fontSize: "clamp(40px, 4.6vw, 60px)"
    fontWeight: 400
    lineHeight: 1.05
    letterSpacing: "-0.035em"
    fontVariation: '"ELSH" 11'
  headline:
    fontFamily: '"Geist Pixel Var", "Geist", sans-serif'
    fontSize: "clamp(30px, 3.6vw, 46px)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-2px"
    fontVariation: '"ELSH" 40'
  title:
    fontFamily: '"Geist", system-ui, sans-serif'
    fontSize: "18px"
    fontWeight: 500
    lineHeight: "24px"
  body:
    fontFamily: '"Geist", system-ui, sans-serif'
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "24px"
  label:
    fontFamily: '"Geist", system-ui, sans-serif'
    fontSize: "13px"
    fontWeight: 500
    lineHeight: "18px"
  mono:
    fontFamily: '"Geist Mono", ui-monospace, monospace'
    fontSize: "12.5px"
    fontWeight: 400
    lineHeight: "18px"
rounded:
  score-bar: "2px"
  output-tag: "5px"
  table: "8px"
  control: "10px"
  surface: "11px"
  field: "12px"
  flow: "14px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "24px"
  2xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 18px"
    height: "44px"
  button-ghost:
    backgroundColor: "{colors.day-tile}"
    textColor: "{colors.day-text}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 16px"
    height: "40px"
  field:
    backgroundColor: "{colors.day-tile}"
    textColor: "{colors.day-text}"
    typography: "{typography.body}"
    rounded: "{rounded.field}"
    padding: "12px 14px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.day-body}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "7px 12px"
  chip-selected:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "7px 12px"
  card:
    backgroundColor: "{colors.day-rail}"
    textColor: "{colors.day-text}"
    rounded: "{rounded.surface}"
    padding: "20px"
  pipeline-stage:
    backgroundColor: "{colors.day-rail}"
    textColor: "{colors.day-text}"
    rounded: "{rounded.flow}"
    padding: "22px 22px 22px 0"
---

# Design System: Antseed Outreach Pipeline

## Overview

**Creative North Star: "The Auditable Waterfall"**

The Antseed system makes a narrowing process visible. Connected bands show how one company becomes a ranked, reachable lead set.

The visual language is calm, exact, and operational. Pixel headings add Antseed character. Flat rails, dotted edges, and direct copy keep the work traceable.

This surface extends the existing Antseed identity. It preserves the lockup, Geist families, green controls, dotted rails, and day and night themes.

**Key Characteristics:**

- A centered rail contains the complete workspace.
- Eight-pixel dot grids define page and section edges.
- Pixel type marks headings and key figures.
- Green marks action, readiness, progress, and focus.
- Connected stage widths show pipeline narrowing.
- Day and night themes keep the same hierarchy.

## Colors

The palette combines agricultural green with warm, low-contrast work surfaces.

### Primary

- **Seed Green** (`primary`): Use for primary actions, ready stages, progress bars, and active filters.
- **Pressed Leaf** (`primary-hover`): Use only for day-theme primary hover states.
- **Night Sprout** (`night-primary`): Use for readable action text and focus marks in the night theme.

### Secondary

- **Acid Seed** (`acid-highlight`): Use only for selected text and rare attention moments.

### Neutral

- **Paper Rail** (`day-rail`) and **Warm Page** (`day-page`): Separate the working rail from the dotted page margin.
- **Near Ink** (`day-title`) and **Field Ink** (`day-text`): Carry headings and operating text in the day theme.
- **Slate Copy** (`day-body`) and **Quiet Copy** (`day-small`): Carry explanations, labels, notes, and metadata.
- **Soft Tile** (`day-tile`) and **Hairline Green** (`day-line`): Define controls and surfaces without heavy boxes.
- **Night Rail** (`night-rail`) and **Night Page** (`night-page`): Preserve the same rail hierarchy after theme changes.
- **Night Ink** (`night-text`) and **Night Quiet** (`night-muted`): Keep night-theme copy readable without pure white everywhere.
- **Failure Red** (`day-error`, `night-error`) and **Warning Amber** (`day-warning`, `night-warning`): Mark status only.

**The Green Means Progress Rule.** Use green for action, focus, readiness, success, and measured progress.

**The Theme Role Rule.** Change token values between themes. Do not change component hierarchy or meaning.

**The Acid Rarity Rule.** Keep acid green out of normal controls. Reserve it for text selection.

## Typography

**Display Font:** Geist Pixel Var, with Geist and sans-serif fallbacks.

**Body Font:** Geist, with system sans-serif fallbacks.

**Label/Mono Font:** Geist Mono, with the system monospace fallback.

**Character:** Pixel type gives Antseed a technical and organic signature. Geist keeps forms and tables direct and calm.

### Hierarchy

- **Display:** Use the pixel display role for the main statement only. Keep the soft opacity and tight tracking.
- **Headline:** Use the pixel headline role for section headings. Use the muted final punctuation as a recurring signature.
- **Title:** Use medium Geist for component titles, company names, and form groups.
- **Body:** Use regular Geist for primary operating text. Keep long explanations below 70 characters per line.
- **Label:** Use medium Geist for fields, buttons, and table headers.
- **Mono:** Use Geist Mono for commands, paths, email addresses, output names, and machine state.

**The Pixel Anchor Rule.** Use Geist Pixel for headings and important figures. Do not use it for dense body text.

**The Data Voice Rule.** Use mono type only when the content behaves like data, code, or system output.

## Layout

The page uses a centered rail with a maximum width of 1312px. Dotted page margins remain visible outside the rail.

Horizontal content padding uses `clamp(20px, 9.64vw, 145px)`. Full sections use 120px vertical padding.

The setup area uses two columns above 1023px. The left summary stays visible while the form moves.

The hero also uses two columns above 1023px. It stacks the summary panel below the copy on smaller screens.

The waterfall centers each stage. Its width reflects the current item count, with a 48 percent minimum for legibility.

At 900px, cards and metrics move to two columns. At 760px, forms, stages, cards, and metrics use one column.

At 760px, the ranking stays a horizontal table. The contacts table becomes a card list.

**The One Rail Rule.** Keep the complete task inside one continuous rail. Do not split it into dashboard islands.

**The Narrowing Rule.** Keep all five stages connected, ordered, and visibly narrower when counts fall.

## Elevation & Depth

The system stays flat by default. Thin borders, surface tone, and dotted boundaries create most depth.

Primary buttons use a small lower edge and inset highlight. Ghost buttons use a quiet inset edge.

Cards rise by 2px on hover. Their border changes to a green-tinted line.

The sticky navigation uses a translucent rail color and 14px backdrop blur.

### Shadow Vocabulary

- **Primary control edge:** `0 3.5px 0.5px rgba(46,74,14,.1), inset 0 -0.5px rgba(200,230,170,.63), inset 0 -2px 1px #3b5e17`. Use only for primary buttons.
- **Ghost control edge:** `inset 0 -1px 2px rgba(48,56,44,.08)`. Use for secondary controls.

**The Flat First Rule.** Use tone and hairlines before shadow. Add lift only for action or hover feedback.

## Shapes

The system uses soft corners and exact circles. Controls use 10px to 12px corners. Stages use 14px corners.

Pills and filters use fully rounded ends. Stage numbers and status marks use circles.

Tables use tighter 8px corners. Small output tags use 5px corners.

Dotted rules use an 8px grid with points below 2px. These dots define the Antseed rail.

**The Soft Precision Rule.** Use moderate curves for controls and surfaces. Do not use oversized rounded containers.

## Components

### Buttons

- **Shape:** Use a 10px corner and a 44px height for the primary button.
- **Primary:** Use Seed Green with white text and 18px horizontal padding.
- **Hover / Focus:** Darken the day button on hover. Use a 2px green focus outline with a 2px offset.
- **Secondary / Ghost:** Use the tile tone, hairline border, and 40px height.
- **Disabled:** Keep the shape. Reduce opacity to 52 percent and remove movement.

### Chips

- **Style:** Use transparent pill controls with quiet text and a hairline border.
- **State:** Fill the selected chip with Seed Green. Use white text for the selected state.

### Cards / Containers

- **Corner Style:** Use 11px corners for result cards and 14px corners for pipeline stages.
- **Background:** Use the rail color for content cards. Use the tile tone for supporting panels.
- **Shadow Strategy:** Keep surfaces flat. Use a 2px hover rise only for cards.
- **Border:** Use one hairline border on each contained surface.
- **Internal Padding:** Use 20px for cards and 22px for stages.

### Inputs / Fields

- **Style:** Use the tile tone, a hairline border, a 12px corner, and 12px by 14px padding.
- **Focus:** Change the border to the theme green. Change the fill to the rail color.
- **Error / Disabled:** Use the error token for status copy. Keep disabled action text visible at reduced opacity.

### Navigation

- **Style:** Keep the Antseed lockup at the left. Keep direct run actions at the right.
- **Surface:** Use a translucent rail background, a hairline lower border, and 14px blur.
- **Mobile:** Hide the route tag before removing actions. Reduce control height below 520px.

### Pipeline Stage

- **Structure:** Show the stage number, question, outputs, count, gate state, note, and action in one band.
- **Ready State:** Tint the border and fill the stage number with Seed Green.
- **Connection:** Use a short green vertical line between stages.
- **Mobile:** Move the state controls below the stage copy. Keep the stage order unchanged.

### Tables

- **Header:** Use small medium text on the tile tone.
- **Rows:** Use 12px by 14px cells and hairline row dividers.
- **Hover:** Use the tile tone across the full row.
- **Responsive:** Scroll rankings horizontally. Convert contacts into cards below 760px.

## Do's and Don'ts

### Do:

- **Do** preserve the Antseed lockup, pixel headings, dotted rails, and both themes.
- **Do** show every stage, gate, count, failure, and output in sequence.
- **Do** use green consistently for action, focus, readiness, and success.
- **Do** keep paid enrichment behind a clear confirmation step.
- **Do** respect reduced-motion settings and visible keyboard focus.
- **Do** keep direct product language and real data labels.

### Don't:

- **Don't** turn the workspace into unrelated dashboard cards.
- **Don't** hide a failed gate or let later stages appear complete after failure.
- **Don't** use the pixel font for paragraphs, form values, or dense tables.
- **Don't** use acid green as a normal button or surface color.
- **Don't** replace dotted structure with heavy borders or large shadows.
- **Don't** change the hierarchy between day and night themes.
