# Math Mentor AI - Frontend Design Document

## 1. Application Overview

**Math Mentor AI** is a multi-agent AI system designed to solve JEE-level mathematics problems. The application combines Vision-Language Models (VLM), Audio Transcription (Whisper), and a structured Agentic Orchestration flow to provide accurate, verified, and detailed step-by-step solutions.

### Core Value Proposition
- **Multi-modal input**: Text, image (OCR), and audio (speech-to-text)
- **Multi-agent verification**: Parser → RAG → Solver → Verifier → Explainer
- **Human-in-the-loop (HITL)**: Low-confidence solutions trigger human review
- **Memory & learning**: Stores solved problems for pattern reuse
- **LaTeX rendering**: Full mathematical notation support

---

## 2. Backend Architecture Summary

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/solve` | POST | Main solving pipeline - accepts text/image/audio |
| `/extract/image` | POST | Upload image → extracted math text |
| `/extract/image/base64` | POST | Base64 image → extracted text |
| `/extract/audio` | POST | Upload audio → transcript |
| `/extract/audio/base64` | POST | Base64 audio → transcript |
| `/hitl/{id}` | POST | Human review response (approve/edit) |
| `/feedback/{id}` | POST | Thumbs up/down feedback |
| `/memory` | GET | List recent solved problems |
| `/memory/{id}` | GET | Single memory record |
| `/health` | GET | Health check + KB status |

### Agent Pipeline (Orchestration Flow)

```
User Input → Parser Agent → RAG Engine → Solver Agent → Verifier Agent → [HITL?] → Explainer Agent → Final Answer
```

**Agents:**
1. **Parser Agent**: Cleans OCR/ASR noise, identifies topic, extracts variables/constraints
2. **Intent Router**: Classifies problem type and routes workflow
3. **Solver Agent**: Generates step-by-step solution using tools (RAG, SymPy, Python)
4. **Verifier Agent**: Checks correctness, assigns confidence score, triggers HITL if < 75%
5. **Explainer Agent**: Produces student-friendly explanation with LaTeX formatting

### Key Data Models

- **ParsedProblem**: problem_text, topic, variables, constraints, needs_clarification
- **SolverResult**: solution, final_answer, tool_calls[]
- **VerifierResult**: is_correct, confidence (0-1), issues[], needs_hitl
- **ExplanationResult**: explanation, final_answer, confidence
- **RetrievedSource**: title, source, section, snippet, score
- **MemoryRecord**: Full problem history with embeddings

---

## 3. Frontend Design Philosophy

### Design Principles

1. **Clarity First**: Math is complex; the UI should not be. Clean layouts, clear typography
2. **Progressive Disclosure**: Show orchestration details only when relevant
3. **Trust but Verify**: Confidence indicators and HITL flows build user trust
4. **Multi-modal Friendly**: Seamless switching between text, image, and audio input
5. **LaTeX Native**: First-class support for mathematical notation

### Visual Style

- **Dark Theme**: Easy on the eyes for long study sessions
- **Accent Color**: Indigo (#6366F1) - associated with knowledge and learning
- **Typography**:
  - Sans: Sora (clean, modern)
  - Mono: IBM Plex Mono (code, math, technical elements)
- **Spacing**: Generous whitespace for readability
- **Border Radius**: Consistent 6-20px for modern feel

### Color Palette

```css
--bg:          #0E0E11;    /* Main background */
--surface:     #15151A;    /* Cards, panels */
--elevated:    #1D1D23;    /* Input bars, buttons */
--border:      #2C2C35;    /* Borders, dividers */
--border-hi:   #4F46E5;    /* Focus states */
--text:        #EDEAE4;    /* Primary text */
--text-2:      #9B9693;    /* Secondary text */
--text-3:      #55524F;    /* Tertiary/muted */
--accent:      #6366F1;    /* Primary accent */
--accent-dim:  #1E1E3F;    /* Accent backgrounds */
--accent-glow: rgba(99,102,241,0.12); /* Glow effects */
--green:       #4DC882;    /* Success, high confidence */
--red:         #E05C5C;    /* Error, low confidence */
--yellow:      #F5A623;    /* Warning, medium confidence */
```

---

## 4. Page Layout & Structure

### Overall Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (Logo + Title + Subtitle)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────┐  ┌─────────────────────────┐  │
│  │                              │  │  Inspector Panel        │  │
│  │   Chat Area                  │  │  ┌─────────────────────┐  │  │
│  │   ┌──────────────────────┐   │  │  │  Tabs:              │  │  │
│  │   │  Message History     │   │  │  │  • History          │  │  │
│  │   │  (Scrollable)        │   │  │  │  • Agent Trace      │  │  │
│  │   └──────────────────────┘   │  │  │  • Context          │  │  │
│  │                              │  │  └─────────────────────┘  │  │
│  │   ┌──────────────────────┐   │  │                           │  │
│  │   │  Input Bar           │   │  │                           │  │
│  │   │  (Text + Attachments)│   │  │                           │  │
│  │   └──────────────────────┘   │  │                           │  │
│  │                              │  └─────────────────────────┘  │
│  └──────────────────────────────┘                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

- **Desktop (≥1024px)**: Full 3-column layout (Chat 7: Inspector 3)
- **Tablet (768-1023px)**: Inspector moves below chat
- **Mobile (<768px)**: Single column, inspector in drawer/modal

---

## 5. Component Specifications

### 5.1 Header

**Elements:**
- Logo: "∑" symbol in accent-colored box
- Title: "MATH MENTOR AI" (mono font, accent color)
- Subtitle: "JEE-level · RAG + Multi-Agent AI" (muted text)

**Behavior:**
- Sticky on scroll
- Minimal height (60px)
- Border-bottom for separation

### 5.2 Chat Area

**Message Bubbles:**
- User messages: Right-aligned, elevated background
- Bot messages: Left-aligned, surface background
- Math content: Rendered with KaTeX
- Code blocks: Syntax highlighted, copy button

**Empty State:**
- Centered placeholder with logo
- Instructions: "Ask a JEE-level math problem"
- Supported topics: algebra · calculus · probability · linear algebra

**Loading States:**
- Skeleton shimmer while processing
- Agent step indicators (Parser → RAG → Solver → Verifier → Explainer)

### 5.3 Input Bar

**Elements:**
- Attachment button (+): Opens file panel
- Text input: Auto-growing textarea
- Send button: Primary accent color

**Features:**
- **Live LaTeX Preview**: Shows rendered math below input as user types `$...$`
- **Drag & Drop**: Support for image/audio files
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for newline
- **Auto-focus**: After sending message

**Attachment Panel:**
- Tabs: Image | Audio
- Image: Upload or paste, preview thumbnail
- Audio: Record button with visualizer or file upload

### 5.4 Inspector Panel (Right Sidebar)

**Tab 1: History**
- List of last 10 solved problems
- Each item: Topic badge, problem preview, final answer
- Click to load into chat
- Refresh button

**Tab 2: Agent Trace**
- Real-time orchestration flow visualization
- Tool calls with expandable details
- Timing information

**Tab 3: Context**
- Retrieved RAG sources
- Relevance scores
- Snippet previews
- Links to full documents

### 5.5 Confidence & Feedback UI

**Confidence Indicator:**
- 🟢 High (≥85%): Green badge
- 🟡 Medium (65-84%): Yellow badge
- 🔴 Low (<65%): Red badge + HITL trigger

**Feedback Strip:**
- 👍 Correct / 👎 Wrong buttons
- Optional comment textarea
- Appears after solution delivery

**HITL Panel:**
- Warning banner: "Our AI Confidence is Low"
- Editable text field for corrections
- Submit / Quick Edit buttons
- Glow border for visibility

---

## 6. User Flows

### Flow 1: Text Input → Solution

```
1. User types math problem in input bar
2. Live LaTeX preview appears below input
3. User presses Enter
4. Message appears in chat with "Solving..." indicator
5. Agent trace updates in real-time (Parser → RAG → Solver → Verifier → Explainer)
6. Solution appears with:
   - Step-by-step explanation (LaTeX rendered)
   - Final Answer box
   - Confidence badge
   - Feedback buttons
```

### Flow 2: Image Upload → Extraction → Solution

```
1. User clicks attachment (+) → selects Image tab
2. User uploads image (drag-drop or click)
3. System extracts text via /extract/image
4. If needs_review:
   - Show extracted text in editable field
   - Confidence indicator
   - "Edit if needed, then click Send"
5. User confirms/edits and sends
6. Continue to solving pipeline
```

### Flow 3: Audio Recording → Transcription → Solution

```
1. User clicks attachment (+) → selects Audio tab
2. User clicks Record button
3. Visualizer shows recording status
4. User stops recording
5. System transcribes via /extract/audio
6. Show transcript with confidence
7. If needs_review: editable field
8. Continue to solving pipeline
```

### Flow 4: Human-in-the-Loop (HITL)

```
1. Verifier returns confidence < 75%
2. HITL panel appears above input bar
3. Warning message displayed
4. User options:
   - Approve: Accept solution as-is
   - Edit: Provide corrected answer
   - Reject: Start over
5. Feedback saved to memory for learning
```

### Flow 5: Memory Reuse

```
1. User asks similar problem to previous one
2. Memory lookup finds similar solved problems
3. System injects past solutions as context
4. Solver may reuse patterns
5. UI shows "Similar problems found" indicator in Context tab
```

---

## 7. State Management

### Global State

```typescript
interface AppState {
  // Chat
  messages: Message[];
  inputText: string;
  isLoading: boolean;

  // Input modes
  activeMode: 'text' | 'image' | 'audio';
  attachedImage: File | null;
  attachedAudio: Blob | null;

  // Extraction
  extractedText: string;
  extractionConfidence: 'high' | 'medium' | 'low';
  needsReview: boolean;

  // Current solution
  memoryId: string | null;
  parsedProblem: ParsedProblem | null;
  solverResult: SolverResult | null;
  verifierResult: VerifierResult | null;
  explanation: ExplanationResult | null;
  retrievedSources: RetrievedSource[];

  // UI state
  showHitl: boolean;
  showFeedback: boolean;
  activeInspectorTab: 'history' | 'trace' | 'context';
  history: MemorySummary[];
}
```

### API Integration

- **HTTP Client**: Fetch/Axios with timeout (120s for solve)
- **Error Handling**: Retry logic, user-friendly error messages
- **Loading States**: Optimistic UI updates

---

## 8. Technical Implementation Notes

### LaTeX Rendering

- **Library**: KaTeX (fast, lightweight)
- **Delimiters**:
  - `$$...$$` for display math
  - `$...$` for inline math
  - `\[...\]` and `\(...\)` for compatibility
- **Live Preview**: Debounced 300ms, render in isolated container

### File Handling

- **Images**: Convert to base64 for API, max 5MB
- **Audio**: WebM/WAV recording, max 25MB
- **Validation**: MIME type check before upload

### Performance Optimizations

- **Virtual Scrolling**: For long chat histories
- **Lazy Loading**: Inspector tabs load on demand
- **Debouncing**: Input preview, resize handlers
- **Memoization**: Expensive math rendering

### Accessibility

- **ARIA Labels**: All interactive elements
- **Keyboard Navigation**: Tab order, shortcuts
- **Screen Readers**: MathML fallback for equations
- **Color Contrast**: WCAG AA compliant

---

## 9. Animation & Interactions

### Micro-interactions

- **Input Bar Focus**: Border color change + subtle glow
- **Send Button Hover**: Scale 1.07x + color shift
- **Message Appear**: Fade in + slide up (200ms ease-out)
- **Agent Step Complete**: Checkmark pulse animation
- **Confidence Badge**: Color-coded pulse on appear

### Loading States

- **Typing Indicator**: Three dots bouncing
- **Agent Progress**: Step-by-step checkmarks
- **Skeleton**: Shimmer effect on placeholders

### Transitions

- **Tab Switch**: 200ms fade
- **Panel Toggle**: 300ms slide + fade
- **HITL Appear**: 400ms slide down + glow pulse

---

## 10. Error Handling

### User-Facing Errors

| Error | Message | Action |
|-------|---------|--------|
| Backend unreachable | "Cannot connect to Math Mentor. Please check your connection." | Retry button |
| Extraction failed | "Could not read image. Try a clearer photo." | Re-upload prompt |
| Timeout | "This problem is taking longer than expected. Try simplifying?" | Cancel/Retry |
| Low confidence | "AI is unsure. Please review the solution." | HITL panel |
| Invalid math | "Could not parse. Check your LaTeX syntax." | Input highlight |

### Recovery Patterns

- **Auto-retry**: 3 attempts with exponential backoff
- **Fallback**: Show partial results if available
- **Offline**: Queue requests, sync when back online

---

## 11. Future Enhancements

### Phase 2 Features

- **Drawing Pad**: Sketch math problems directly
- **Step-by-step Toggle**: Expand/collapse solution steps
- **Bookmarking**: Save favorite problems
- **Export**: PDF/PNG of solutions
- **Share**: Link to specific problem solutions

### Phase 3 Features

- **Real-time Collaboration**: Study groups
- **Progress Tracking**: Stats dashboard
- **Gamification**: Streaks, achievements
- **Mobile App**: Native iOS/Android

---

## 12. File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Main chat interface
│   │   └── globals.css         # Global styles + CSS variables
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── input/
│   │   │   ├── InputBar.tsx
│   │   │   ├── AttachmentPanel.tsx
│   │   │   ├── ImageUploader.tsx
│   │   │   ├── AudioRecorder.tsx
│   │   │   └── LatexPreview.tsx
│   │   ├── inspector/
│   │   │   ├── InspectorPanel.tsx
│   │   │   ├── HistoryTab.tsx
│   │   │   ├── AgentTraceTab.tsx
│   │   │   └── ContextTab.tsx
│   │   ├── feedback/
│   │   │   ├── ConfidenceBadge.tsx
│   │   │   ├── FeedbackStrip.tsx
│   │   │   └── HitlPanel.tsx
│   │   └── shared/
│   │       ├── Header.tsx
│   │       ├── Logo.tsx
│   │       └── MathRenderer.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useExtraction.ts
│   │   ├── useSolve.ts
│   │   └── useMemory.ts
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── utils.ts            # Utilities
│   │   └── latex.ts            # LaTeX helpers
│   ├── types/
│   │   └── index.ts            # TypeScript types
│   └── store/
│       └── index.ts            # State management
├── public/
│   └── fonts/                  # Custom fonts
├── docs/
│   └── frontend-design.md      # This document
└── package.json
```

---

## 13. API Integration Reference

### Example: Solve Request

```typescript
const solveProblem = async (input: SolveRequest) => {
  const response = await fetch(`${API_URL}/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      input_type: 'text', // or 'image' | 'audio'
      content: 'Solve: x^2 + 5x + 6 = 0',
      filename: null
    })
  });

  const data: SolveResponse = await response.json();
  return data;
};
```

### Example: Image Extraction

```typescript
const extractImage = async (base64Image: string) => {
  const response = await fetch(`${API_URL}/extract/image/base64`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_data: base64Image,
      mime_type: 'image/png'
    })
  });

  const data: ExtractionResponse = await response.json();
  return data;
};
```

---

## 14. Testing Checklist

### Functional Tests

- [ ] Text input solves correctly
- [ ] Image upload extracts and solves
- [ ] Audio recording transcribes and solves
- [ ] HITL flow triggers on low confidence
- [ ] Feedback submission works
- [ ] History loads and displays
- [ ] Agent trace shows tool calls
- [ ] Context tab shows RAG sources

### UI Tests

- [ ] LaTeX renders correctly in messages
- [ ] Live preview updates while typing
- [ ] Responsive layout on mobile/tablet
- [ ] Dark theme consistent across components
- [ ] Loading states appear appropriately
- [ ] Error messages are user-friendly

### Performance Tests

- [ ] Chat scrolls smoothly with 50+ messages
- [ ] Image upload handles 5MB files
- [ ] Audio recording works for 60+ seconds
- [ ] LaTeX preview debounces correctly
- [ ] Memory list loads in < 500ms

---

*Document Version: 1.0*
*Last Updated: March 2026*
*Author: AI Assistant*
