# SPRINT-16 — Component Refactoring & Full-Stack Coverage

**Sprint**: 16  
**Dates**: TBD  
**Epic**: EPIC-013  
**Scrum Master**: Scrum Master Agent  
**Planned velocity**: 11 story points

---

## Sprint Goal

> Refactor sidebar component to enable line-level unit coverage, verify the CI  
> coverage-docker job end-to-end, and reduce the unit suite runtime.

---

## Sprint Backlog

| Story     | Title                                                    | Points | Status        | Assigned        |
| --------- | -------------------------------------------------------- | ------ | ------------- | --------------- |
| US-071    | Refactor sidebar: extract pure logic from widget calls   | 5      | 🔲 Not Started | Developer       |
| US-072    | Add unit tests for extracted sidebar logic               | 3      | 🔲 Not Started | Unit Test Agent |
| US-073    | Verify coverage-docker job on GitHub Actions test branch | 2      | 🔲 Not Started | DevOps          |
| US-074    | Investigate pytest-xdist parallel execution              | 1      | 🔲 Not Started | DevOps          |
| **Total** |                                                          | **11** |               |                 |

---

## Definition of Ready

- [ ] EPIC-013 approved
- [ ] US-071 through US-074 written and accepted
- [ ] Architecture review for sidebar refactoring approach complete

---

## Carry-Over

None. Sprint 15 closed cleanly at 11/11 pts.

---

## Risks

| Risk                                           | Likelihood | Impact | Mitigation                                                  |
| ---------------------------------------------- | ---------- | ------ | ----------------------------------------------------------- |
| Sidebar refactor breaks AppTest smoke tests    | Medium     | High   | Keep smoke tests running throughout; refactor incrementally |
| GitHub Actions runner not available for US-073 | Low        | Low    | Use a fork branch or draft PR to trigger the CI workflow    |
