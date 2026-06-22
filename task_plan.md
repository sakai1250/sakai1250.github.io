# Task Plan: Ivory Editorial Portfolio

## Goal

Implement the approved Ivory Editorial redesign while preserving the portfolio’s content and interaction behavior.

## Phases

- [x] Phase 1: Approve and document the design
- [x] Phase 2: Write the implementation plan
- [x] Phase 3: Add failing regression tests
- [x] Phase 4: Implement HTML/CSS/JS changes
- [x] Phase 5: Verify desktop, dark theme, interactions, and mobile
- [x] Phase 6: Review and deliver

## Key Questions

1. Are all existing DOM hooks and interaction paths preserved?
2. Are cyber styling and drag behavior fully removed without removing approved effects?
3. Does the result remain readable and responsive in Japanese and English?

## Decisions Made

- Visual direction: A. Ivory Editorial.
- Initial theme: follow OS preference unless a saved theme exists.
- Remove only card drag/reorder; retain other effects after reducing intensity.
- Use dependency-free static regression tests plus browser verification.

## Errors Encountered

- In-app browser bootstrap failed because required sandbox metadata was unavailable. Used local headless Chrome and Chrome DevTools Protocol instead.
- A CLI screenshot at `390x844` used a 500px internal viewport and appeared cropped. Verified the exact 390px layout with device metrics override; document width was 390px with no overflow.

## Status

**Complete** - Implementation, responsive checks, interaction checks, and final diff review finished.

## Interaction Restoration

- [x] Add failing tests for avatar drag guidance and visible 3D card tilt
- [x] Restore avatar drag guidance without restoring card/list reordering
- [x] Increase application-card tilt to a restrained maximum of 4 degrees
- [x] Verify drag target text, return animation, card transform, and browser errors
- [x] Restore drag rotation for profile and section cards without DOM reordering
- [x] Verify rotation, release reset, unchanged parent/count, and app modal behavior
