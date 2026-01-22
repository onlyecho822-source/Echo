# I'M TELLING — Submit a Question

<div align="center">

### *Not snitching. Setting the record straight.*

**PUBLIC VERIFICATION REQUEST PORTAL**

*You ask. We verify. We're telling.*

---

[![Submissions](https://img.shields.io/badge/Submissions-OPEN-brightgreen?style=for-the-badge)]()
[![Response Time](https://img.shields.io/badge/Response-24--72_Hours-blue?style=for-the-badge)]()

</div>

---

## What Can You Ask?

Submit any claim you want verified:

| Category | Examples |
|----------|----------|
| **Political Claims** | "Did they really say that?" "How did they vote?" |
| **Economic Data** | "Are those unemployment numbers real?" |
| **Official Statements** | "Is this quote accurate or out of context?" |
| **Historical Records** | "What actually happened?" |
| **Media Claims** | "Is this story accurate?" |

---

## What We Don't Verify

| Category | Reason |
|----------|--------|
| **Personal Disputes** | Not within scope |
| **Opinions** | Can't verify subjective claims |
| **Future Predictions** | Can't verify what hasn't happened |
| **Unverifiable Claims** | Need sources that can be checked |

---

## How to Submit

### Option 1: GitHub Issue (Preferred)

1. Go to the repository Issues tab
2. Click "New Issue"
3. Title: `[I'M TELLING] Your topic here`
4. Fill out the template below
5. Submit

**[Create Issue Now →](../../issues/new?title=[I'M%20TELLING]%20Your%20topic%20here)**

---

### Option 2: Full Submission Template

Copy and complete:

```markdown
# I'M TELLING — VERIFICATION REQUEST

## Submission ID
[Leave blank - assigned upon receipt]

## Date
[YYYY-MM-DD]

## Submitter
[Your GitHub username or "Anonymous"]

---

## THE CLAIM

### What's the claim?
[Exact quote or precise description]

### Who made it?
[Person, organization, media outlet]

### When was it made?
[Date/time if known]

### Where did you see it?
[URL, broadcast, speech, etc.]

---

## SOURCES YOU KNOW OF

### Supporting (if any)
1. [URL or reference]
2. [URL or reference]

### Contradicting (if any)
1. [URL or reference]
2. [URL or reference]

---

## WHY IT MATTERS

[Brief explanation — why should this be verified?]

## URGENCY

[ ] Routine — No rush
[ ] Timely — Relevant to current events
[ ] Urgent — Decision depends on this

---

## ANYTHING ELSE?
[Additional context]
```

---

### Option 3: Quick Submit

For simple questions:

```
CLAIM: [The exact claim]
WHO SAID IT: [Person/org]
WHEN: [Date]
SOURCE: [Where you saw it]
```

---

## What Happens Next

```
┌─────────────────────────────────────────────────────────────────┐
│                  I'M TELLING VERIFICATION PIPELINE              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. INTAKE                                                     │
│      └── Your submission is logged with unique ID               │
│      └── Status: PENDING                                        │
│                                                                 │
│   2. TRIAGE                                                     │
│      └── We assess if it's verifiable                           │
│      └── Status: QUEUED                                         │
│                                                                 │
│   3. INVESTIGATION                                              │
│      └── We find primary sources                                │
│      └── Status: IN PROGRESS                                    │
│                                                                 │
│   4. VERIFICATION                                               │
│      └── We triangulate (minimum 3 sources)                     │
│      └── Status: UNDER REVIEW                                   │
│                                                                 │
│   5. WE'RE TELLING                                              │
│      └── Report published with full proof                       │
│      └── Status: VERIFIED / DISPUTED / CONTESTED                │
│                                                                 │
│   6. ARCHIVED FOREVER                                           │
│      └── Stored in immutable ledger                             │
│      └── Status: ARCHIVED                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Response Times

| Priority | Target |
|----------|--------|
| **Routine** | 72 hours |
| **Timely** | 24-48 hours |
| **Urgent** | 12-24 hours |

*Complex verifications may take longer.*

---

## Track Your Submission

All submissions are tracked in `submissions/`:

```
submissions/
├── pending/       ← Waiting to be processed
├── in-progress/   ← Currently investigating
└── completed/     ← Done — check the result
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `PENDING` | Received, waiting |
| `QUEUED` | Accepted, in line |
| `IN_PROGRESS` | We're on it |
| `UNDER_REVIEW` | Almost done |
| `VERIFIED` | ✅ Claim confirmed |
| `DISPUTED` | ❌ Claim contradicts evidence |
| `CONTESTED` | ⚠️ Sources conflict |
| `REJECTED` | Can't verify / out of scope |
| `ARCHIVED` | Permanently stored |

---

## Anonymous Submissions

Yes, you can submit anonymously. Just put "Anonymous" in the Submitter field.

We don't collect:
- Personal info
- Email (unless you give it)
- IP addresses

---

## Examples

### Example 1: Political Statement

```
CLAIM: "Mayor X said 'we will not raise taxes' on January 10"
WHO SAID IT: Mayor X
WHEN: January 10, 2026
SOURCE: Local news broadcast

WHY IT MATTERS: They just proposed a tax increase
```

### Example 2: Voting Record

```
CLAIM: "Senator Y voted for Bill Z"
WHO SAID IT: Campaign advertisement
WHEN: January 15, 2026
SOURCE: TV ad

WHY IT MATTERS: Their opponent says they voted against it
```

### Example 3: Out of Context Quote

```
CLAIM: "Official said 'I don't care about the people'"
WHO SAID IT: Social media posts
WHEN: January 18, 2026
SOURCE: Viral video clip

WHY IT MATTERS: Need to know if this is the full quote or edited
```

---

## FAQ

**Q: Is it free?**  
A: Yes. Public verification is free.

**Q: Can I be anonymous?**  
A: Yes.

**Q: What if you can't verify it?**  
A: We'll tell you why and mark it as unverifiable.

**Q: What if I disagree with your result?**  
A: Submit additional sources. We consider all evidence.

**Q: How do I know you're not biased?**  
A: We publish all sources and methodology. Verify it yourself.

---

## Submit Now

**[Create GitHub Issue →](../../issues/new?title=[I'M%20TELLING]%20Your%20topic%20here)**

Or use the templates above.

---

<div align="center">

# I'M TELLING

### *Not snitching. Setting the record straight.*

**You ask. We verify. We're telling.**

---

*"If they lied, we're telling. If they didn't, we're telling that too."*

</div>
