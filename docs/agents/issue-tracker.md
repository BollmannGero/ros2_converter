# Issue tracker: GitHub

Issues and specs live in GitHub Issues for
`BollmannGero/ros2_converter`. Use the `gh` CLI from this repository.

## Conventions

- Verify the target before the first issue creation of a session:
  `gh repo view --json nameWithOwner`.
  The expected repository is `BollmannGero/ros2_converter`.
  If it differs, resolve the target before writing.
- Create: `gh issue create --title "..." --body-file <file>`.
  For multiline bodies and comments, write the exact text to a temporary
  UTF-8 file and pass it with `--body-file`.
- Read: `gh issue view <number> --json number,title,body,labels,comments`.
- List: `gh issue list --state open --json number,title,body,labels`.
  Add label and state filters as needed.
- Comment: `gh issue comment <number> --body-file <file>`.
- Apply or remove labels:
  `gh issue edit <number> --add-label "..."` or `--remove-label "..."`.
- Close: post the explanation as a comment, then
  `gh issue close <number>`. Post comments separately even when the
  issue is already closed.
- Sub-issues: use native GitHub sub-issues when supported by the
  installed CLI/API. Otherwise, add `Part of #<parent>` to the child
  body and link it from a task list in the parent.
- Blocking: use native GitHub issue dependencies when supported.
  Otherwise, add `Blocked by: #<number>, #<number>` to the child body.
  Work can start when every blocker is closed.

File issues only in the user's repository.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Read the GitHub issue, including its comments.

## Wayfinding operations

- Map: one issue labelled `wayfinder:map`, containing Notes,
  Decisions-so-far, and Fog.
- Child ticket: link it to the map using the sub-issue convention above.
  Label it `wayfinder:research`, `wayfinder:prototype`,
  `wayfinder:grilling`, or `wayfinder:task`.
- Frontier: select the first open child in map order with no open
  blockers and no assignee.
- Claim: `gh issue edit <number> --add-assignee "@me"`.
- Resolve: comment with the answer, close the ticket, and append a
  summary and link to the map's Decisions-so-far.
