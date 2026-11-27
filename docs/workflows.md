# Shared workflows

Tessaly-dev/.github holds three reusable workflows. Each repository calls them with its own `GITHUB_TOKEN`, so no personal access token or app secret exists.

| Workflow | What it does | Permissions |
| --- | --- | --- |
| `reusable-labels.yml` | Syncs labels from `labels.yml` | `contents: read`, `issues: write` |
| `reusable-stale.yml` | Closes `status: pending-info` issues after 21 quiet days and pull requests after 44 | `issues: write`, `pull-requests: write` |
| `reusable-triage.yml` | Keeps one status label per issue, reopens triage when the reporter replies, closes duplicates | `issues: write` |

## Which repositories use them

Every public repository in Tessaly-dev calls all three, except homebrew-tap, which only the release workflow writes to and which takes no issues. Add a new repository to this table when you add its caller files.

| Repository | Labels | Stale | Triage |
| --- | --- | --- | --- |
| [.github](https://github.com/Tessaly-dev/.github) | yes | yes | yes |
| [tessaly](https://github.com/Tessaly-dev/tessaly) | yes | yes | yes |
| [tessaly.dev](https://github.com/Tessaly-dev/tessaly.dev) | yes | yes | yes |
| [extensions](https://github.com/Tessaly-dev/extensions) | yes | yes | yes |

The labels are the same everywhere, so an issue moved between repositories keeps its labels.

## Add them to a repository

Create these three files in the repository. Pin `<sha>` to a commit on `main` of Tessaly-dev/.github. Dependabot bumps the pin.

```yaml
# .github/workflows/labels.yml
name: Labels
on:
  schedule:
    - cron: "17 4 * * 1"
  workflow_dispatch:
permissions: {}
jobs:
  sync:
    permissions:
      contents: read
      issues: write
    uses: Tessaly-dev/.github/.github/workflows/reusable-labels.yml@<sha>
```

```yaml
# .github/workflows/stale.yml
name: Stale
on:
  schedule:
    - cron: "23 3 * * *"
  workflow_dispatch:
permissions: {}
jobs:
  stale:
    permissions:
      issues: write
      pull-requests: write
    uses: Tessaly-dev/.github/.github/workflows/reusable-stale.yml@<sha>
```

```yaml
# .github/workflows/triage.yml
name: Triage
on:
  issues:
    types: [opened, labeled]
  issue_comment:
    types: [created]
permissions: {}
jobs:
  triage:
    permissions:
      issues: write
    uses: Tessaly-dev/.github/.github/workflows/reusable-triage.yml@<sha>
```

## Security rules

- Every action is pinned to a full commit SHA, with the version in a comment.
- Each workflow sets `permissions: {}` at the top and grants each job only what it uses.
- No workflow uses `pull_request_target` or runs code from a pull request.
- Issue titles, bodies and comments are read through the API as data and never reach a shell.
- Only first-party actions run: `actions/checkout`, `actions/stale` and `actions/github-script`.
