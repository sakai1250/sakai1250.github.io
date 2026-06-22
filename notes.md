# Notes: Ivory Editorial Portfolio

## Existing structure

- Static site: `index.html`, `style.css`, `main.js`, `effects.js`.
- Core selectors are already stable and must remain unchanged.
- Current cyber presentation is concentrated in CSS tokens/backgrounds and `effects.js`.
- Drag behavior is initialized from `main.js` and implemented in `effects.js`.

## Verification approach

- Node built-in tests will inspect source contracts without adding dependencies.
- Browser verification will cover visual hierarchy, responsive layout, and interactions.
- `.superpowers/` is a temporary brainstorming artifact and must remain outside the implementation commit.

## Verification results

- Static regression tests: 5/5 passed.
- JavaScript syntax: `main.js` and `effects.js` passed `node --check`.
- Exact mobile viewport: 390x844, document `clientWidth` and `scrollWidth` both 390.
- Mobile header stats and primary tabs: left 16px, right 374px, width 358px.
- Mobile profile card appears before main content and uses `#071A2F`.
- Light body background resolved to `#F7F3EA`.
- Dark body background and theme token resolved to `#09131F`.
- EN/JA toggle, Engineering tab, 2025 filter, theme toggle, app modal open/close all passed through Chrome DevTools Protocol.
- Browser runtime errors: none.

## Interaction restoration

- Restored the top-left avatar drag guide as `initAvatarDragGuide()`, independently from removed card/list reordering.
- Dragging over the profile card showed `プロフィール・連絡先`; releasing restored the avatar position and hid the tooltip.
- Increased application-card tilt to a maximum of 4 degrees with a 4px lift. Browser verification observed approximately 3.7 degrees at the tested pointer position.
- Card/list drag reordering, handles, placeholders, and drop targets remain removed.
- Restored drag rotation for `.profile-card` and `.section-card` independently from reordering.
- Browser drag verification observed `rotateX(-10.375deg) rotateY(11.725deg)` and a 6.96px lift.
- After release, the transform cleared, the section remained under `#research-content`, and the section count remained 6.
- Clicking an application card still opened its modal after the drag-rotation change.
