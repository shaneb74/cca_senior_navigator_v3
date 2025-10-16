# AI Advisor Page - Navi Redesign 2.0

**Branch:** `navi-redesign-2`  
**Date:** October 16, 2025  
**Status:** ✅ Complete

## Overview

Complete redesign of the FAQs & Answers page to showcase Navi as the app's prominent expert advisor. The new design emphasizes clean minimalism, Navi's signature blue accent color, and smart contextual guidance.

---

## What Changed

### 1. **Page Identity & Branding**
- **Title:** "AI Advisor" (clean, professional)
- **Intro:** "I'm Navi — your expert advisor."
- **Contextual Description:** "Ask about care options, costs, benefits, and next steps. I'll point you to the right tools."
- **Visual Hierarchy:** Clear H1 → Subhead → Description structure
- **Navi's Blue:** `#4A90E2` used for intro text and UI accents without overwhelming the page

### 2. **Suggested Questions (Refreshable Chips)**
- **Display:** 3-6 question chips in responsive grid
- **Behavior:** Click → Submit question → Auto-refresh chip set with new questions
- **Smart Rotation:** 
  - Tracks recently asked questions (last 10)
  - Avoids duplicates
  - Resets pool when user has asked most questions
- **Topics:** Each question tagged by topic (planning, safety, veterans, costs, benefits)

### 3. **Ask Me Anything (Fake GPT Flow)**
- **Text Input:** Clean input field with placeholder guidance
- **Send Button:** Primary action button (supports Enter key)
- **Clear Chat:** Resets conversation for current session only
- **Typing Indicator:** "✨ Navi is thinking..." for 600-900ms before response
- **Keyword Matching:** Maps user input to templated answers from question database
- **Fallback Response:** Helpful default when no match found, with topic suggestions

### 4. **Response Quality**
- **Format:** Short, skimmable, action-oriented (bullets > paragraphs)
- **Cross-Links:** Every response includes at least one module reference
  - Example: "Check eligibility with the VA Benefits module in Cost Planner."
- **Structure:**
  - Bold headings for key points
  - Bullet lists for clarity
  - Specific cost ranges and timeframes
  - Clear next actions

### 5. **Minimalist Styling**
- **Layout Width:** 840px max-width, centered content column
- **Clean Hierarchy:**
  - H1: AI Advisor
  - Subhead: "I'm Navi — your expert advisor."
  - Sections: Suggested Questions, Ask Me Anything, Questions I've Asked
- **Message Bubbles:**
  - User: Plain text bubble with gray background
  - Navi: Card with ✨ icon, soft blue tint (`#F5F8FF`), subtle border
- **Question Chips:** Pill buttons with quiet outline, hover → fill effect
- **Whitespace:** Generous vertical rhythm (24-32px between sections)
- **Responsive:** Mobile-optimized with smaller fonts and tighter spacing

### 6. **Behavior Details**
- **Session Persistence:** Conversation history survives page navigation within session
- **Clear Chat:** Wipes only this page's conversation (doesn't affect other app state)
- **Rate Limiting:** Typing indicator prevents rapid-fire spam
- **No Banners:** Clean page with no colored strips or promotional content
- **Accessibility:**
  - Proper ARIA labels for inputs and buttons
  - Visible focus states on interactive elements
  - `prefers-reduced-motion` support (disables animations)

### 7. **Microcopy Excellence**
- **Navi Intro:** "Ask about care options, costs, benefits, and next steps. I'll point you to the right tools."
- **Module Cross-Links:** "Check eligibility with the VA Benefits module in Cost Planner."
- **Guardrail Footer:** "Navi offers information, not medical or legal advice." (subtle, small text)
- **Empty State:** "💡 Click a suggested question above or type your own to start chatting with Navi."

### 8. **Navigation**
- **Back to Hub:** Single button at bottom, full-width, subdued style
- **In-App Navigation:** All links stay in-app (no new tabs)
- **Consistent Routing:** Uses `route_to("hub_concierge")` like other products

---

## Technical Implementation

### Files Changed

| File | Changes | Lines Changed |
|------|---------|---------------|
| `pages/ai_advisor.py` | ✨ NEW - Complete redesign of AI Advisor page | +500 |
| `pages/_stubs.py` | Updated `render_faqs()` to point to new module | 2 |

### Key Components

#### 1. Question Database
```python
QUESTION_DATABASE = {
    "question_key": {
        "question": "Display text",
        "topic": "planning|safety|veterans|costs|benefits",
        "keywords": ["match", "terms"],
        "response": "Formatted markdown response with **bold** and bullets"
    }
}
```

- **12 Core Questions:** Covering care planning, safety, veterans, costs, benefits
- **Topic Tags:** Enable smart grouping and rotation
- **Keyword Matching:** Flexible natural language matching
- **Action-Oriented:** Every response includes module cross-links

#### 2. Suggestion Engine
```python
def _get_suggested_questions(exclude: List[str]) -> List[str]:
    """Get 3-6 suggested questions, excluding recently asked."""
```

- Filters out recently asked questions (tracked in `ai_asked_keys`)
- Shuffles available questions for variety
- Resets pool when < 3 questions available
- Returns 3-6 questions for responsive grid

#### 3. Response Matching
```python
def _match_question(user_input: str) -> Optional[Dict]:
    """Match user input via exact match or keyword matching."""
```

- Try exact question match first
- Fall back to keyword matching
- Return fallback response if no match

#### 4. Typing Indicator
```python
def _render_typing_indicator():
    """Show 'Navi is thinking...' for 600-900ms."""
    with st.spinner("✨ Navi is thinking..."):
        time.sleep(random.uniform(0.6, 0.9))
```

- Random delay (600-900ms) feels natural
- Prevents spam by rate-limiting responses

### CSS Architecture

**Custom Classes:**
- `.faq-container` — 840px max-width, centered
- `.faq-header` — Page title and intro
- `.faq-chip` — Suggested question pill button
- `.faq-message--user` — User message bubble
- `.faq-message--navi` — Navi response card with icon
- `.faq-guardrail` — Footer disclaimer

**Design Tokens:**
- Navi Blue: `#4A90E2`
- Navi Background: `#F5F8FF`
- Border: `#E0E7FF`
- Chip Hover Shadow: `rgba(74, 144, 226, 0.15)`

**Animations:**
- `fadeInUp` — Message bubbles appear with subtle slide-up
- Chip hover — Translate up 1px with shadow
- Respects `prefers-reduced-motion`

---

## Question Coverage

### Topics Covered
1. **Care Planning** (3 questions)
   - Where to start
   - Next steps after assessments
   - Family conversations

2. **Safety & Urgency** (2 questions)
   - Fall risk prevention
   - Memory care vs. assisted living

3. **Veterans** (1 question)
   - VA Aid & Attendance eligibility

4. **Costs & Funding** (4 questions)
   - Home care costs
   - How to afford care
   - Medicaid coverage
   - Home equity options

5. **Benefits** (2 questions)
   - Medicare coverage
   - Medicaid eligibility

### Module Cross-Links
Every response links to relevant modules:
- ✅ **Guided Care Plan** — Assess needs
- ✅ **Cost Planner** — Estimate costs, explore funding
- ✅ **VA Benefits module** — Check eligibility
- ✅ **Medicaid Navigation module** — Understand eligibility
- ✅ **Plan with My Advisor** — Book expert consultation

---

## Session State Management

### State Keys
```python
st.session_state["ai_thread"]          # [(role, message), ...]
st.session_state["ai_asked_keys"]      # ["question_key", ...]
st.session_state["ai_current_input"]   # User's current input (for clearing)
```

### Persistence
- ✅ **Within Session:** History survives navigation to other pages
- ✅ **Clear Chat:** Resets only AI Advisor conversation
- ❌ **Across Sessions:** Cleared on browser refresh (by design)

---

## Acceptance Criteria

### ✅ Functional Requirements
- [x] Clicking suggested question submits it and refreshes chip set
- [x] Answers include at least one module/tool cross-link
- [x] No colored banners on page
- [x] Session history persists until Clear chat or session end
- [x] Typing indicator shows for 600-900ms
- [x] Enter key submits question
- [x] Clear chat resets conversation

### ✅ UI/UX Requirements
- [x] Page title: "AI Advisor"
- [x] Intro: "I'm Navi — your expert advisor."
- [x] Contextual description (Concierge Hub specific)
- [x] 3-6 suggested question chips
- [x] Clean minimalist layout (840px max-width)
- [x] Navi's signature blue without overwhelming page
- [x] Message bubbles: user plain, Navi with icon and tint
- [x] Generous whitespace (24-32px vertical rhythm)
- [x] Accessible: labels, focus states, reduced motion support

### ✅ Content Requirements
- [x] Responses are short, skimmable, bullet-focused
- [x] Action-oriented with clear next steps
- [x] Cross-links to modules in app
- [x] Guardrail footer: "Navi offers information, not medical or legal advice."
- [x] Fallback response with topic suggestions

### ✅ Navigation Requirements
- [x] Single "Back to Hub" button at bottom
- [x] All navigation stays in-app (no new tabs)
- [x] Consistent routing with other products

---

## Testing Checklist

### Functional Testing
- [ ] Click suggested question → submits and refreshes chips
- [ ] Type question and click Send → shows typing indicator → displays response
- [ ] Press Enter in input field → submits question
- [ ] Click Clear chat → clears conversation only
- [ ] Navigate to another page → return → conversation persists
- [ ] Ask 10+ questions → chip pool resets properly
- [ ] Try unmatched question → shows fallback response
- [ ] Click module cross-links → navigates correctly

### UI/Visual Testing
- [ ] Page loads with clean, centered layout
- [ ] Navi's blue accent appears but doesn't overwhelm
- [ ] Message bubbles render correctly (user vs. Navi)
- [ ] Chips display in responsive grid (wraps on mobile)
- [ ] Hover states work on chips and buttons
- [ ] Focus states visible for accessibility
- [ ] Empty state shows when no messages
- [ ] Guardrail footer appears at bottom

### Responsive Testing
- [ ] Desktop (1440px+): Full 840px width, 3-column chip grid
- [ ] Tablet (768-1024px): Adjusted spacing, 2-column chips
- [ ] Mobile (< 768px): Single column, smaller fonts, touch-friendly

### Accessibility Testing
- [ ] Screen reader announces page title and sections
- [ ] Input has proper label (hidden visually, accessible to AT)
- [ ] Focus order is logical (chips → input → buttons → messages)
- [ ] Focus visible on all interactive elements
- [ ] `prefers-reduced-motion` disables animations
- [ ] Color contrast meets WCAG AA standards

---

## Migration Notes

### From Old FAQ Page
The previous `pages/faq.py` used:
- Flag-driven question selection via `NaviOrchestrator`
- Large question database with priority levels
- Topic tags for matching

The new `pages/ai_advisor.py` simplifies:
- Curated set of 12 high-quality questions
- Topic-based grouping for chip rotation
- Cleaner keyword matching
- Focus on visual design and UX

### Backward Compatibility
- ✅ `render_faqs()` in `_stubs.py` still works (delegates to new module)
- ✅ Navigation config unchanged (still points to `render_faqs`)
- ✅ Session state keys different (won't conflict with old implementation)

---

## Future Enhancements

### Phase 2 (Optional)
1. **Smart Context Detection**
   - Read GCP flags to suggest relevant questions
   - Detect Cost Planner completion to shift question topics

2. **Enhanced Matching**
   - Use fuzzy string matching for better keyword detection
   - Add synonym support (e.g., "Medicaid" vs. "medical aid")

3. **Answer Personalization**
   - Insert user's name from session state
   - Reference their specific care recommendation
   - Show cost estimates from their Cost Planner

4. **Analytics**
   - Track most-asked questions
   - Identify questions with no good match
   - Log user satisfaction (thumbs up/down on responses)

5. **Rich Responses**
   - Add images or diagrams to complex topics
   - Embed video clips for visual learners
   - Link to external resources (articles, tools)

---

## Design Rationale

### Why This Approach?

#### 1. Minimalist Layout
**Goal:** Let Navi's personality shine without visual clutter.
- Centered 840px column creates comfortable reading width
- Generous whitespace prevents cognitive overload
- Clean hierarchy guides user through page flow

#### 2. Navi's Blue Accent
**Goal:** Brand recognition without overwhelming the page.
- `#4A90E2` used sparingly (intro text, borders, hover states)
- Soft tint (`#F5F8FF`) for Navi response bubbles
- White background keeps page light and airy

#### 3. Chip-Based Suggestions
**Goal:** Encourage exploration without analysis paralysis.
- 3-6 chips provide choice without overwhelming
- One-click action reduces friction
- Auto-refresh keeps experience fresh

#### 4. Typing Indicator
**Goal:** Human-like interaction, rate limiting, anticipation.
- 600-900ms feels natural (not instant, not slow)
- Prevents spam by forcing pause between questions
- Creates anticipation for response

#### 5. Session-Scoped History
**Goal:** Continuity within session, clean slate on new visit.
- User can reference previous answers while exploring
- Clear chat gives control to reset conversation
- No server-side storage needed (privacy-friendly)

---

## Success Metrics

### User Engagement
- **Target:** 3+ questions asked per session
- **Target:** 50%+ of users click suggested questions
- **Target:** < 10% fallback responses (good keyword matching)

### Navigation Patterns
- **Track:** Most common question topics
- **Track:** Module cross-links clicked (measure intent to take action)
- **Track:** Sessions where user navigates to module after AI Advisor

### UX Quality
- **Target:** 0 accessibility errors (WCAG AA)
- **Target:** < 2s page load time
- **Target:** Mobile-friendly (no horizontal scroll, touch targets ≥ 44px)

---

## Deployment

### Ready for Testing
```bash
# On branch: navi-redesign-2
streamlit run app.py

# Navigate to FAQs/AI Advisor from Concierge Hub
```

### Ready for Commit
```bash
git add pages/ai_advisor.py pages/_stubs.py
git commit -m "feat: Complete AI Advisor page redesign (Navi 2.0)

- Clean minimalist layout with 840px read width
- Navi's signature blue accent without overwhelming
- 3-6 refreshable question chips with smart rotation
- Typing indicator (600-900ms) for natural feel
- Session-persistent conversation history
- 12 curated questions covering planning, safety, costs, benefits
- Every response includes module cross-links
- Accessible: labels, focus states, reduced motion support
- Mobile-responsive design"
```

---

## Questions & Feedback

### Design Questions
- Should we add thumbs up/down for response quality?
- Should Clear chat confirm before wiping history?
- Should we persist conversation across sessions (localStorage)?

### Content Questions
- Are 12 questions enough, or should we expand to 20+?
- Should responses be even shorter (more bullet-focused)?
- Should we add "Related Questions" at end of each response?

### Technical Questions
- Should we integrate with real GPT API in future?
- Should we track analytics (question frequency, fallback rate)?
- Should we add search/filter for question database?

---

## Summary

✅ **Complete redesign of AI Advisor page**  
✅ **Navi as the prominent, helpful expert**  
✅ **Clean, minimalist design with signature blue**  
✅ **Smart question suggestions with rotation**  
✅ **Action-oriented responses with module cross-links**  
✅ **Accessible, responsive, and user-friendly**  
✅ **Ready for testing and deployment**

**Next Steps:** Test thoroughly, gather feedback, iterate on content quality and question coverage.
