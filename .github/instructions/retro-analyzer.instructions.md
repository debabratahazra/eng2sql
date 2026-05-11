---
applyTo: "docs/sprints/*-retro.md"
---

# Retro Analyzer — Authoring Rules

These rules apply whenever any agent reads or writes a `SPRINT-*-retro.md` file or any
artifact that the Retro Analyzer creates from it.

---

## Sprint Retro File Requirements

Every `docs/sprints/SPRINT-<N>-retro.md` MUST contain these four sections in this order:

```markdown
## What Went Well
## What Could Be Improved
## Action Items
## Cumulative Velocity
```

The **Action Items** section MUST be a Markdown table with exactly these three columns:

```markdown
| Action | Owner | Due |
| ------ | ----- | --- |
```

Permitted `Owner` values (controls what artifact the Retro Analyzer creates):
- `Developer` — code fix or new feature implementation
- `Epic Writer` — new epic required
- `Scrum Master` — sprint planning item
- `Product` — product backlog / roadmap item (no artifact, roadmap only)
- `Architect` — architecture decision required

Permitted `Due` values:
- `Sprint <N> planning` — added to sprint N planning
- `Sprint <N>` — must be done by sprint N
- `Next PR / housekeeping` — small fix, added as a User Story with 1 pt
- `Future backlog` — appended to roadmap Future Backlog only; no sprint assigned
- `Future sprint` — same as `Future backlog`

---

## Processed-Retro Marker

When the Retro Analyzer finishes processing `SPRINT-<N>-retro.md`, it MUST add a line
to the `PROJECT_PROGRESS.md` Agent Activity Log that contains exactly:

```
Retro Analyzer | Processed SPRINT-<N>-retro.md
```

This exact string is how subsequent runs detect whether a retro has been processed.
Do NOT change this format.

---

## Bug Report Naming

Bug files created from retros MUST follow:

```
docs/bug-reports/BUG-<NNN>-<kebab-slug-max-5-words>.md
```

Slugs must be lowercase, hyphen-separated, derived from the bug title. No underscores.

---

## User Story Naming

User stories created from retros MUST follow:

```
docs/user-stories/sprint-<N>/US-<NNN>-<kebab-slug-max-5-words>.md
```

They MUST include this field in their front-matter table:

```markdown
**Source**: Retro — SPRINT-<N>-retro.md
```

---

## Epic Naming

Epics created from retros MUST follow:

```
docs/epics/EPIC-<NNN>-<kebab-slug-max-5-words>.md
```

They MUST include this HTML comment on line 3:

```html
<!-- Source: SPRINT-<N>-retro.md Action Items -->
```

---

## ID Sequencing — Never Reuse or Skip

- Epic IDs, US IDs, and Bug IDs are globally unique integers, zero-padded to 3 digits.
- The Retro Analyzer MUST scan all existing files to determine the next available ID.
- IDs must be strictly sequential — no gaps, no duplicates.
- If two retros are processed in the same run, the second retro's artifacts use IDs that
  follow on from the first retro's artifacts (not from the pre-run state).

---

## Retro-to-Sprint Mapping

| Retro File | Creates Artifacts For |
|------------|----------------------|
| `SPRINT-N-retro.md` | Sprint N+1 (plan, stories, bugs) |

If Sprint N+1 already has a plan file, append to it. Do not overwrite.

---

## Classification Precedence

When an action item could be either a Bug or a User Story, prefer:
- **Bug** if the text describes existing broken behaviour.
- **User Story** if the text describes behaviour that is missing but never promised.

When an item could be either a User Story or an Epic:
- **Epic** if the action item explicitly names a new multi-sprint theme.
- **User Story** if it can be completed within a single 2-week sprint.

---

## Roadmap Update Rules

- Never delete existing roadmap rows — only append or update status symbols.
- Sprint tables in the roadmap use `✅` for done, `🔲` for planned, `🔄` for in-progress.
- Future Backlog bullets must end with `*(source: SPRINT-<N>-retro.md)*`.
- The Epic Progress percentage is recalculated as `done_stories / total_stories * 100`.
