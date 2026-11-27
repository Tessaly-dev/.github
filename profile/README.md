<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="tessaly-logo-dark.svg">
    <img alt="Tessaly logo: four agents fitting together into a T" src="tessaly-logo-light.svg" width="140">
  </picture>
</p>

<h1 align="center">Tessaly</h1>

<p align="center">Run many coding agents in parallel, on your own machine.</p>

Tessaly is an open source, local-first tool for running coding agents side by side. Each agent gets its own git worktree, so they never step on each other. You review the diffs, open the pull requests and keep everything on hardware you control.

- Runs any CLI agent you set up, such as Claude Code or Codex, in a live terminal in your browser
- A home view of what needs you, and a board of every workspace
- Diff review, and pull requests on GitHub with their CI checks
- Resume an agent that a restart cut off
- One Go binary with a browser UI, on your own machine or in Docker

Security comes first. Tessaly listens on 127.0.0.1 by default, requires sign-in with a passkey or a login token, and never sends your code to a cloud service of its own.

## Repositories

| Repository | What it is |
| --- | --- |
| [tessaly](https://github.com/tessaly-dev/tessaly) | The daemon, CLI (`tess`) and web UI. |
| [tessaly.dev](https://github.com/tessaly-dev/tessaly.dev) | The website and docs at [tessaly.dev](https://tessaly.dev). Coming soon. |
| [extensions](https://github.com/tessaly-dev/extensions) | The signed index of community extensions. Coming soon. |
| [homebrew-tap](https://github.com/tessaly-dev/homebrew-tap) | The Homebrew tap. Releases update it. |
| [.github](https://github.com/tessaly-dev/.github) | This profile, the default community files, and the shared labels and workflows for every repo. |

## Get involved

- Read the [contributing guide](https://github.com/tessaly-dev/.github/blob/main/CONTRIBUTING.md) before your first pull request.
- Report security issues privately to security@tessaly.dev. See the [security policy](https://github.com/tessaly-dev/.github/blob/main/SECURITY.md).
- Everything else: hello@tessaly.dev or [tessaly.dev](https://tessaly.dev).

Tessaly is licensed under Apache-2.0 and maintained by 86-88 Solutions.
