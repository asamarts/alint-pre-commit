# alint-pre-commit

A [pre-commit](https://pre-commit.com) hook mirror for
[alint](https://github.com/asamarts/alint), the repository-structure linter. It
installs the prebuilt `alint` wheel from PyPI (fast, no Rust toolchain) and
exposes alint's hooks.

## Usage

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/asamarts/alint-pre-commit
    rev: v0.16.1 # replace with the latest tag, or run `pre-commit autoupdate`
    hooks:
      - id: alint # `alint check` (non-mutating)
      # - id: alint-fix   # `alint fix` (mutating; runs only on the manual stage)
```

Then:

```bash
pre-commit run --all-files
```

`alint` reads `.alint.yml` at your repo root and walks the tree honoring
`.gitignore`. The same hook works for any language's repository, since alint
lints structure, not code.

## What this repo is

It carries no alint source. It is a thin `language: python` front-end whose
`pyproject.toml` pins `alint==<version>`; pre-commit installs that wheel into the
hook environment and runs the `alint` binary from it. This is the same model
`ruff-pre-commit` uses for ruff.

`mirror.py` (run daily by CI, and on demand) re-pins to the newest alint on PyPI
and tags `v<version>`, so a `rev` only ever points at a version whose wheel is
live. Tags appear once alint is published to PyPI.

## License

This mirror's glue is MIT (see `LICENSE`). alint itself is dual-licensed
MIT OR Apache-2.0.
