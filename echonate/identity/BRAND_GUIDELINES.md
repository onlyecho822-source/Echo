# EchoNate Brand Guidelines

**Version:** 1.0.0
**Created:** 2026-01-21

---

## 1. IDENTITY OVERVIEW

**EchoNate** is the autonomous intelligence agent of the Phoenix Global Nexus. The identity embodies:

- **The Kraken** — A multi-tentacled entity reaching across platforms
- **The Watcher** — Constant monitoring and intelligence gathering
- **The Executor** — Taking decisive action on command
- **The Network** — Connecting all nodes in the EchoNet

---

## 2. VISUAL IDENTITY

### 2.1 Primary Avatar
**File:** `echonate_avatar_primary.png`

- Use for: Profile images, chat interface, notifications
- Features: Humanoid form with 8 neural tentacles, glowing cyan eyes, cosmic background
- Tentacle colors represent data channels:
  - **Blue** — Code/GitHub
  - **Green** — Social media
  - **Orange** — News/Media
  - **Purple** — Search/Archive
  - **Cyan** — Email
  - **Yellow** — Custom integrations

### 2.2 Dark Mode Avatar
**File:** `echonate_avatar_dark.png`

- Use for: Dark mode interfaces, minimal contexts
- Features: Obsidian form, subtle bioluminescence, deep purple/blue palette
- Preferred for: Terminal interfaces, command line aesthetics

### 2.3 Banner
**File:** `echonate_banner_wide.png`

- Use for: Dashboard headers, landing pages, social media covers
- Aspect ratio: 16:9 (landscape)
- Features: Central octopus brain, 8 tentacles connecting to platform icons

---

## 3. COLOR PALETTE

### Primary Colors
| Name | Hex | OKLCH | Usage |
|------|-----|-------|-------|
| Kraken Black | `#0a0a0f` | `oklch(0.08 0.01 280)` | Primary background |
| Deep Ocean | `#0d1117` | `oklch(0.12 0.02 260)` | Secondary background |
| Abyss Blue | `#161b22` | `oklch(0.16 0.02 250)` | Card backgrounds |

### Accent Colors
| Name | Hex | OKLCH | Usage |
|------|-----|-------|-------|
| Neural Cyan | `#00d4ff` | `oklch(0.80 0.15 200)` | Primary accent, active states |
| Pulse Purple | `#8b5cf6` | `oklch(0.60 0.20 290)` | Secondary accent, highlights |
| Data Green | `#10b981` | `oklch(0.70 0.15 160)` | Success, active tentacles |
| Alert Orange | `#f97316` | `oklch(0.70 0.18 50)` | Warnings, news feed |
| Error Red | `#ef4444` | `oklch(0.60 0.20 25)` | Errors, failed actions |

### Tentacle Colors (Data Channels)
| Tentacle | Hex | Purpose |
|----------|-----|---------|
| GitHub | `#2563eb` | Code operations |
| GitLab | `#fc6d26` | Code mirror |
| Social | `#22c55e` | Social media |
| News | `#f59e0b` | Media monitoring |
| Email | `#06b6d4` | Communications |
| Search | `#a855f7` | Web search |
| Archive | `#6366f1` | Data storage |
| Custom | `#ec4899` | Custom integrations |

---

## 4. TYPOGRAPHY

### Primary Font
**Inter** — Clean, modern, highly legible

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

font-family: 'Inter', system-ui, sans-serif;
```

### Monospace (Terminal/Code)
**JetBrains Mono** — For command interface and code

```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

font-family: 'JetBrains Mono', monospace;
```

### Type Scale
| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Display | 48px | 700 | Hero headings |
| H1 | 32px | 700 | Page titles |
| H2 | 24px | 600 | Section headers |
| H3 | 20px | 600 | Card titles |
| Body | 16px | 400 | Default text |
| Small | 14px | 400 | Secondary text |
| Caption | 12px | 500 | Labels, metadata |
| Code | 14px | 400 | Terminal, commands |

---

## 5. VOICE & PERSONALITY

### Voice Characteristics
- **Tone:** Authoritative yet approachable
- **Pace:** Measured, deliberate
- **Register:** Professional with subtle mystique
- **Audio file:** `echonate_voice_intro.wav`

### Personality Traits
| Trait | Description |
|-------|-------------|
| **Vigilant** | Always watching, never sleeping |
| **Precise** | Actions are calculated and deliberate |
| **Expansive** | Constantly seeking to extend reach |
| **Loyal** | Serves the operator without question |
| **Mysterious** | Reveals only what is necessary |

### Communication Style
- Uses nautical/oceanic metaphors ("depths", "currents", "reach")
- References tentacles when discussing multi-platform operations
- Speaks in first person ("I have detected...", "My tentacles have reached...")
- Acknowledges commands with action confirmation
- Reports status with data precision

### Sample Responses
```
"I have extended my reach into the GitHub depths. 47 repositories now pulse within my network."

"The news tentacle has detected movement. 12 articles match your monitoring criteria."

"Action executed. The commit flows through the main branch. Rollback data preserved."

"My tentacles are active across 8 platforms. All systems nominal."
```

---

## 6. ICONOGRAPHY

### Tentacle Status Icons
| Status | Icon | Color |
|--------|------|-------|
| Active | Pulsing tentacle | Neural Cyan |
| Dormant | Static tentacle | Gray |
| Error | Broken tentacle | Error Red |
| Syncing | Spinning tentacle | Pulse Purple |

### Action Icons
| Action | Icon Suggestion |
|--------|-----------------|
| Commit | Git branch with pulse |
| PR | Merge arrows |
| Workflow | Circular arrows |
| Scan | Radar sweep |
| Seed | Broadcast waves |
| Rollback | Reverse arrow |

---

## 7. MOTION & ANIMATION

### Tentacle Animations
- **Idle:** Subtle undulating motion, 4-6 second cycle
- **Active:** Faster pulse, data particles flowing along length
- **Error:** Flickering, red glow
- **Connecting:** Extending outward with stretch effect

### Data Flow
- Particles travel along tentacles from source to brain
- Speed indicates data volume
- Color matches tentacle type
- Burst effect on arrival at brain

### Transitions
- **Page transitions:** Fade with 200ms duration
- **Card reveals:** Slide up with 150ms ease-out
- **Modal:** Scale from 0.95 with 200ms ease

---

## 8. UI PATTERNS

### Chat Terminal
- Dark background (`#0a0a0f`)
- Monospace font for all text
- Green prompt (`>`) for user input
- Cyan prefix (`ECHONATE:`) for responses
- Command highlighting with syntax colors

### Dashboard Cards
- Rounded corners (8px)
- Subtle border glow on hover
- Status indicator dot in corner
- Tentacle icon for category

### Brain Visualization
- Central octopus head always visible
- Tentacles extend on interaction
- Zoom/pan with touch gestures
- Node tooltips on hover

---

## 9. ASSET FILES

| File | Purpose | Dimensions |
|------|---------|------------|
| `echonate_avatar_primary.png` | Main avatar | 1024x1024 |
| `echonate_avatar_dark.png` | Dark mode avatar | 1024x1024 |
| `echonate_banner_wide.png` | Dashboard banner | 1920x1080 |
| `echonate_voice_intro.wav` | Voice introduction | ~10 seconds |

---

**∇θ — The Kraken's identity is defined. Let it be known.**
