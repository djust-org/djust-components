# Release Process

This document describes how to create releases for djust-components.

## Version Numbering

djust-components follows [Semantic Versioning](https://semver.org/) (SemVer) with [PEP 440](https://peps.python.org/pep-0440/) compatible pre-release suffixes.

### Version Format

```
MAJOR.MINOR.PATCH[{a|b|rc}N]
```

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)
- **a**: Alpha (early testing)
- **b**: Beta (feature complete, testing)
- **rc**: Release candidate (final testing)

### Examples

```
0.3.0      # Stable patch release
0.4.0a1    # Alpha 1 (early testing of 0.4.0 features)
0.4.0b1    # Beta 1 (feature complete, testing)
0.4.0rc1   # Release candidate 1 (final testing)
0.4.0      # Stable release
```

### Installation

```bash
pip install djust-components           # Latest stable (e.g., 0.3.0)
pip install djust-components --pre     # Latest including pre-releases
pip install djust-components==0.4.0rc1 # Specific pre-release
```

## Release Workflow

### 1. Prepare the Release

1. **Create a release branch** (for major/minor releases):
   ```bash
   git checkout main
   git pull
   git checkout -b release/0.4.0
   ```

2. **Update version numbers**:
   ```bash
   make version VERSION=0.4.0rc1
   ```

3. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to a new versioned section
   - Add the release date

4. **Commit and push**:
   ```bash
   git add pyproject.toml src/djust_components/__init__.py CHANGELOG.md
   git commit -m "chore: bump version to 0.4.0rc1"
   git push origin release/0.4.0
   ```

5. **Create PR and merge to main**

### 2. Create the Release

1. **Verify and tag**:
   ```bash
   make version-check
   make release-dry-run VERSION=0.4.0rc1
   make release VERSION=0.4.0rc1
   ```

2. **GitHub Actions will automatically**:
   - Build the package
   - Create a GitHub Release
   - Publish to PyPI

### 3. Post-Release

1. **Verify the release**:
   ```bash
   pip install djust-components==0.4.0rc1
   python -c "import djust_components; print(djust_components.__version__)"
   ```

2. **Update dependent projects** (djust.org, djustlive) if needed

## Makefile Commands

```bash
# Bump version (updates pyproject.toml and __init__.py)
make version VERSION=0.4.0rc1

# Check current version in all files
make version-check

# Show what would be released (dry run)
make release-dry-run VERSION=0.4.0rc1

# Create and push a release tag
make release VERSION=0.4.0rc1

# Run tests
make test
```

## Hotfix Releases

For urgent fixes to stable releases:

1. Branch from the release tag:
   ```bash
   git checkout -b hotfix/0.3.1 v0.3.0
   ```

2. Apply fix, update version to `0.3.1`

3. Tag and release:
   ```bash
   make version VERSION=0.3.1
   make release VERSION=0.3.1
   ```

4. Merge fix back to main and any active release branches
