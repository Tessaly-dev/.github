# Contributing to Tessaly

Thanks for helping. The full guide lives in the main repository: [tessaly-dev/tessaly CONTRIBUTING.md](https://github.com/tessaly-dev/tessaly/blob/main/CONTRIBUTING.md) (coming soon).

The short version:

1. Security first. Report vulnerabilities privately, see [SECURITY.md](SECURITY.md).
2. Keep code simple. Prefer the Go standard library and small interfaces.
3. Add tests with every change. A bug fix includes a test that fails before the fix.
4. Update the docs in the same pull request when behaviour changes.
5. Sign off every commit (`git commit -s`) to agree to the [Developer Certificate of Origin](https://developercertificate.org/).

## How we triage issues

Every repository in Tessaly-dev shares one set of labels, defined in [labels.yml](labels.yml).

1. A new issue gets `status: needs-triage` from the issue form, or from the triage bot if it was opened another way.
2. A maintainer adds one `type:` label, one or more `area:` labels and a `priority:` label, then sets `status: triaged`.
3. When someone starts work, the status becomes `status: in-progress`. Use `status: blocked` when the work waits on something else.
4. If we need more details, a maintainer sets `status: pending-info`. When the reporter replies, the bot moves the issue back to `status: needs-triage`.
5. An issue stays open while it is valid, however old it is. The stale bot only closes:
    - issues with `status: pending-info` and no reply for 21 days (marked stale after 14, closed 7 days later)
    - pull requests with no activity for 44 days (marked stale after 30, closed 14 days later); drafts are skipped
6. Issues and pull requests labelled `security`, `pinned`, `priority: critical`, `status: in-progress` or `status: blocked` are never marked stale.
7. Before you open an issue, check the possible duplicates GitHub suggests on the new issue form. If a maintainer adds `duplicate`, the bot closes the issue with the duplicate reason. Follow the original issue instead.

Each issue has exactly one `status:` label. Adding a new one removes the old one.

Looking for a place to start? Try issues labelled `good first issue` or `help wanted`.

### Changing labels

Open a pull request that edits `labels.yml`. The Check workflow validates the file and prints what would change. After merge, the Labels workflow in each repository creates, updates or renames labels. It never deletes a label. Unknown labels show up in the run log so a maintainer can remove them by hand.

Run the checks locally with:

```sh
python3 -m unittest discover -s scripts
```

Contributions are licensed under Apache-2.0.
