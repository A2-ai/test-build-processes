# GoReleaser Pro Configuration

This document explains the GoReleaser Pro features used in this project's deb package release pipeline.

## Overview

We use **GoReleaser Pro** to create Debian packages (.deb) and tar.gz archives from pre-built Rust binaries. The binaries are built on AlmaLinux 8 containers to ensure glibc 2.28 compatibility, then packaged by GoReleaser Pro.

## GoReleaser Pro Features Used

### 1. Prebuilt Binaries

**Feature:** `prebuilt` in builds configuration
**Documentation:** https://goreleaser.com/customization/prebuilt/

**Why we use it:**
- Our Rust binaries are built in a separate CI stage on AlmaLinux 8 containers
- This ensures binaries are linked against glibc 2.28 for broad Linux compatibility
- Avoids cross-compilation issues when building for multiple architectures
- GoReleaser doesn't need Rust toolchain or cargo installed

**Configuration in `.goreleaser.yml`:**
```yaml
builds:
  - id: test-build-processes
    binary: test-build-processes
    prebuilt:
      path: "{{ .Path }}"
    goos:
      - linux
    goarch:
      - amd64    # x86_64
      - arm64    # aarch64
```

**How it works:**
1. Build stage creates binaries:
   - `dist/test-build-processes_linux_amd64` (from x86_64-unknown-linux-gnu)
   - `dist/test-build-processes_linux_arm64` (from aarch64-unknown-linux-gnu)

2. GoReleaser Pro discovers these pre-built binaries based on naming convention:
   - Pattern: `{binary}_{goos}_{goarch}`
   - The `{{ .Path }}` template tells GoReleaser where to find them

3. GoReleaser packages these binaries without rebuilding them

### 2. NFPM (Debian Packages)

**Feature:** `nfpms` configuration
**Documentation:** https://goreleaser.com/customization/nfpm/

**What it does:**
- Creates `.deb` packages from the prebuilt binaries
- Includes post-installation and pre-removal hooks
- Sets proper file permissions and installation paths

**Configuration:**
```yaml
nfpms:
  - id: test-build-processes-deb
    package_name: test-build-processes
    formats: [deb]
    bindir: /usr/local/bin
    scripts:
      postinstall: scripts/postinstall.sh
      preremove: scripts/preremove.sh
```

**Hooks:**
- `postinstall.sh`: Runs after package installation (e.g., set permissions, create config dirs)
- `preremove.sh`: Runs before package removal (e.g., cleanup)

### 3. Archives

**Feature:** `archives` configuration
**Documentation:** https://goreleaser.com/customization/archive/

**What it does:**
- Creates tar.gz archives containing the binary and documentation files
- Alternative installation method to .deb packages

**Configuration:**
```yaml
archives:
  - id: test-build-processes-archive
    format_overrides:
      - goos: linux
        format: tar.gz
    files:
      - README.md
      - LICENSE*
      - CLAUDE.md
```

### 4. Release Management

**Feature:** `release` configuration
**Documentation:** https://goreleaser.com/customization/release/

**What it does:**
- Creates GitHub releases automatically
- Uploads all artifacts (.deb, .tar.gz, checksums)
- Adds custom release notes and metadata

**Configuration:**
```yaml
release:
  draft: true
  prerelease: auto
  header: |
    Welcome to release {{ .Tag }}!
    [Custom release notes...]
```

## Workflow Integration

### GitHub Actions Setup

We use the `goreleaser/goreleaser-action@v6` action:

```yaml
- name: Run GoReleaser Pro
  uses: goreleaser/goreleaser-action@v6
  with:
    distribution: goreleaser-pro
    version: "~> v2"
    args: release --clean
  env:
    GORELEASER_KEY: ${{ secrets.GORELEASER_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Environment variables:**
- `GORELEASER_KEY`: Pro license key (stored in GitHub Secrets)
- `GITHUB_TOKEN`: For creating releases and uploading assets

### Pipeline Flow

1. **Build-Binaries** job (runs on AlmaLinux 8):
   - x86_64: `ubuntu-latest` → AlmaLinux 8 container
   - aarch64: `ubuntu-24.04-arm` → AlmaLinux 8 container
   - Outputs: Binary artifacts uploaded to GitHub Actions

2. **Package-Deb** job (runs on ubuntu-latest):
   - Downloads both binary artifacts
   - Renames to GoReleaser prebuilt naming convention
   - Runs GoReleaser Pro to create .deb and .tar.gz
   - GoReleaser automatically creates GitHub release (if tag)

## Benefits

1. **No cross-compilation**: Builds run natively on target architecture
2. **glibc compatibility**: Building on AlmaLinux 8 ensures glibc 2.28+
3. **Clean separation**: Build logic separate from packaging logic
4. **Professional packaging**: .deb files with proper hooks and metadata
5. **Multi-format**: Both .deb (for apt/dpkg) and .tar.gz (universal)
6. **Automated releases**: GoReleaser handles GitHub release creation

## Alternative Approaches Considered

### nfpm directly
- **Issue**: Requires running on each architecture separately, complicates workflow
- **Solution**: GoReleaser Pro's prebuilt feature handles multi-arch in single job

### GoReleaser (non-Pro) with Rust builder
- **Issue**: Cross-compilation difficulties, can't control build environment
- **Solution**: Build separately on AlmaLinux, use Pro's prebuilt feature

### Multi-stage Docker builds
- **Issue**: More complex, requires maintaining Dockerfiles
- **Solution**: Use GitHub Actions matrix with containers + GoReleaser Pro

## References

- [GoReleaser Pro Prebuilt Documentation](https://goreleaser.com/customization/prebuilt/)
- [NFPM Documentation](https://goreleaser.com/customization/nfpm/)
- [GoReleaser Pro Pricing](https://goreleaser.com/pro/)
- [GitHub Actions: goreleaser-action](https://github.com/goreleaser/goreleaser-action)
