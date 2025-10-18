# Release Processes

This repository demonstrates two different release pipelines for distributing the Rust binary.

## Release Pipeline 1: Simple Binary Release

**Workflow:** `.github/workflows/release.yml`
**Trigger:** Tags matching `v*.*.*` (e.g., `v0.1.0`)

### Overview
This is a straightforward release process that builds the Rust binary on AlmaLinux 8 containers and packages them as tar.gz archives.

### Process
1. **Build Stage**: Builds binaries for both x86_64 and aarch64 architectures in AlmaLinux 8 containers
2. **Release Stage**: Creates a GitHub release with the tar.gz archives

### Artifacts
- `test-build-processes-v*-x86_64-unknown-linux-gnu.tar.gz`
- `test-build-processes-v*-aarch64-unknown-linux-gnu.tar.gz`

### Usage
```bash
# Trigger a release
git tag v0.1.0
git push origin v0.1.0

# Install from tarball
tar -xzf test-build-processes-v0.1.0-x86_64-unknown-linux-gnu.tar.gz
sudo mv test-build-processes /usr/local/bin/
```

---

## Release Pipeline 2: Debian Package Release

**Workflow:** `.github/workflows/release-deb.yml`
**Trigger:** Tags matching `deb-v*.*.*` (e.g., `deb-v0.1.0`)

### Overview
This is a more sophisticated multi-stage release process that builds binaries on AlmaLinux 8 and then uses nfpm to create .deb packages with installation hooks.

### Process
1. **Build Stage**: Builds binaries for both architectures in AlmaLinux 8 containers
2. **Package Stage**: Uses nfpm on native runners to create:
   - .deb packages with post-install/pre-remove hooks
   - tar.gz archives
3. **Release Stage**: Creates a GitHub release with all artifacts and checksums

### Key Features
- **Installation Hooks**:
  - `postinstall.sh` - Runs after package installation
  - `preremove.sh` - Runs before package removal
- **Proper Package Management**: Integrates with apt/dpkg
- **Multi-Stage Build**: Separates binary compilation from package assembly

### Artifacts
- `test-build-processes_*_amd64.deb` - Debian package for x86_64
- `test-build-processes_*_arm64.deb` - Debian package for ARM64
- `test-build-processes_*_linux_amd64.tar.gz` - Tarball for x86_64
- `test-build-processes_*_linux_arm64.tar.gz` - Tarball for ARM64
- `checksums.txt` - SHA256 checksums for all artifacts

### Usage
```bash
# Trigger a deb release
git tag deb-v0.1.0
git push origin deb-v0.1.0

# Install from .deb package (automatically runs post-install hooks)
sudo dpkg -i test-build-processes_0.1.0_amd64.deb

# Uninstall (automatically runs pre-remove hooks)
sudo apt remove test-build-processes
```

---

## Comparison

| Feature | Simple Binary Release | Deb Package Release |
|---------|----------------------|---------------------|
| **Tag Pattern** | `v*.*.*` | `deb-v*.*.*` |
| **Build Environment** | AlmaLinux 8 | AlmaLinux 8 → GoReleaser |
| **Stages** | 2 (Build + Release) | 3 (Build + Package + Release) |
| **Package Formats** | tar.gz | .deb + tar.gz |
| **Installation Hooks** | No | Yes (post-install, pre-remove) |
| **Package Manager** | Manual | apt/dpkg integration |
| **Uninstall Support** | Manual | Automated via package manager |
| **Checksums** | No | Yes (SHA256) |
| **Use Case** | Quick distribution | Enterprise Linux environments |

---

## Why Two Pipelines?

These two pipelines demonstrate different approaches to software distribution:

1. **Simple Binary Release** is ideal for:
   - Quick releases
   - Users who want minimal dependencies
   - Systems without package managers
   - Direct binary distribution

2. **Deb Package Release** is ideal for:
   - Debian/Ubuntu-based systems
   - Enterprise environments with package management requirements
   - When you need installation/removal hooks
   - Better integration with system package managers
   - Automated dependency management

Both pipelines build on AlmaLinux 8 to ensure glibc 2.28+ compatibility across modern Linux distributions.
