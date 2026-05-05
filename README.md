# prcheck

> GitHub Action that auto-labels PRs based on changed file paths and diff size thresholds

## Installation

```bash
pip install prcheck
```

## Usage

Add the following to your workflow file (e.g. `.github/workflows/prcheck.yml`):

```yaml
name: PR Check

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run prcheck
        uses: your-org/prcheck@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config: .github/prcheck.yml
```

Define your labeling rules in `.github/prcheck.yml`:

```yaml
labels:
  - name: "frontend"
    paths:
      - "src/ui/**"
      - "*.css"
  - name: "large-pr"
    diff_threshold: 500
  - name: "backend"
    paths:
      - "src/api/**"
      - "src/db/**"
```

Labels are applied automatically when a PR is opened or updated based on the changed file paths and total diff line count.

## Configuration

| Option | Description | Default |
|---|---|---|
| `token` | GitHub token for labeling | required |
| `config` | Path to config file | `.github/prcheck.yml` |
| `diff_threshold` | Max lines before `large-pr` label | `500` |

## License

MIT © [your-org](https://github.com/your-org)