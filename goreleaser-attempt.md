# GoReleaser Pro Prebuilt Binaries Attempt

This document chronicles the attempt to use GoReleaser Pro's prebuilt binaries feature for the deb package release pipeline. This approach was ultimately unsuccessful but is documented here for future reference.

## Goal

Use GoReleaser Pro to package pre-built Rust binaries (built on AlmaLinux 8) into .deb packages and tar.gz archives, avoiding the need to rebuild binaries in the packaging stage.

## Why This Approach Was Attempted

1. **Single packaging job**: Instead of per-architecture runners, use one job to package all architectures
2. **Professional tooling**: GoReleaser Pro provides robust packaging, checksums, and release management
3. **Avoid cross-compilation**: Binaries built on native AlmaLinux 8 containers, packaged later
4. **Multi-format support**: Single tool for .deb, tar.gz, and GitHub releases

## Configuration Attempted

### `.goreleaser.yml` (Final Version)

```yaml
version: 2

# Use prebuilt binaries feature (GoReleaser Pro)
builds:
  - id: test-build-processes
    binary: test-build-processes
    dir: "."
    # Tell GoReleaser to use pre-built binaries instead of building
    prebuilt:
      path: dist/{{ .Binary }}_{{ .Os }}_{{ .Arch }}{{ if .Arm }}v{{ .Arm }}{{ end }}{{ if .Mips }}_{{ .Mips }}{{ end }}/{{ .Binary }}{{ .Ext }}
    goos:
      - linux
    goarch:
      - amd64
      - arm64
    goamd64:
      - v1
    goarm64:
      - v8.0

archives:
  - id: test-build-processes-archive
    format_overrides:
      - goos: linux
        format: tar.gz
    name_template: >-
      {{ .ProjectName }}_
      {{- .Version }}_
      {{- .Os }}_
      {{- .Arch }}
    files:
      - README.md
      - LICENSE*
      - CLAUDE.md

nfpms:
  - id: test-build-processes-deb
    package_name: test-build-processes
    vendor: a2-ai
    homepage: https://github.com/a2-ai/test-build-processes
    maintainer: a2-ai Team
    description: |
      test-build-processes - A minimal Rust binary application
      Demonstrates multi-architecture builds and .deb package generation
    license: MIT
    formats:
      - deb
    bindir: /usr/local/bin
    file_name_template: >-
      {{ .ProjectName }}_
      {{- .Version }}_
      {{- .Arch }}
    scripts:
      postinstall: scripts/postinstall.sh
      preremove: scripts/preremove.sh
    contents:
      - src: scripts/postinstall.sh
        dst: /usr/share/doc/test-build-processes/postinstall.sh
        type: config
      - src: scripts/preremove.sh
        dst: /usr/share/doc/test-build-processes/preremove.sh
        type: config
```

### Workflow Preparation Step

```yaml
- name: Prepare prebuilt binaries for GoReleaser
  run: |
    # Create directory structure that GoReleaser expects for prebuilt binaries
    # Format: dist/{binary}_{os}_{arch}_v{version}/{binary}
    mkdir -p dist/test-build-processes_linux_amd64_v1
    mkdir -p dist/test-build-processes_linux_arm64_v8.0

    # Copy x86_64 binary
    cp artifacts/binary-x86_64-unknown-linux-gnu/test-build-processes-x86_64-unknown-linux-gnu \
       dist/test-build-processes_linux_amd64_v1/test-build-processes
    chmod +x dist/test-build-processes_linux_amd64_v1/test-build-processes

    # Copy aarch64 binary
    cp artifacts/binary-aarch64-unknown-linux-gnu/test-build-processes-aarch64-unknown-linux-gnu \
       dist/test-build-processes_linux_arm64_v8.0/test-build-processes
    chmod +x dist/test-build-processes_linux_arm64_v8.0/test-build-processes

    # List the structure for debugging
    ls -R dist/
```

### GoReleaser Invocation

```yaml
- name: Run GoReleaser Pro
  uses: goreleaser/goreleaser-action@v6
  with:
    distribution: goreleaser-pro
    version: "~> v2"
    args: release --clean --skip=validate
  env:
    GORELEASER_KEY: ${{ secrets.GORELEASER_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## What Worked

1. **Binary placement**: Binaries were correctly placed in the expected directory structure:
   ```
   dist/
   ├── test-build-processes_linux_amd64_v1/
   │   └── test-build-processes
   └── test-build-processes_linux_arm64_v8.0/
       └── test-build-processes
   ```

2. **GoReleaser Pro installation**: Successfully downloaded and installed v2.12.5

3. **Configuration validation**: GoReleaser parsed the configuration without syntax errors

4. **Multi-stage workflow**: Successfully built binaries on AlmaLinux 8 and downloaded artifacts

## The Problem

GoReleaser Pro consistently attempted to build the binaries despite the `prebuilt` configuration:

```
building binaries
  • building binary=dist/test-build-processes_linux_arm64_v8.0/test-build-processes
  • building binary=dist/test-build-processes_linux_amd64_v1/test-build-processes
  ⨯ release failed after 0s
    error=
  │ build failed: build for test-build-processes does not contain a main function
  │ Learn more at https://goreleaser.com/errors/no-main
    target=linux_arm64_v8.0
```

**Error Analysis:**
- GoReleaser looked for a Go `main` function (expected for Go projects)
- The `prebuilt` directive was not preventing the build step
- Binaries existed in the correct location but were ignored

## Attempts Made to Fix

### Attempt 1: Basic prebuilt configuration
```yaml
prebuilt:
  path: "{{ .Path }}"
```
**Result**: Still tried to build, looking for main function

### Attempt 2: Explicit path template
```yaml
prebuilt:
  path: dist/{{ .Binary }}_{{ .Os }}_{{ .Arch }}{{ if .Arm }}v{{ .Arm }}{{ end }}/{{ .Binary }}{{ .Ext }}
```
**Result**: Still tried to build

### Attempt 3: Add `dir` field
```yaml
dir: "."
prebuilt:
  path: dist/...
```
**Result**: Still tried to build

### Attempt 4: Add architecture variant specifications
```yaml
goamd64: [v1]
goarm64: [v8.0]
```
**Result**: Still tried to build

### Attempt 5: Use `--skip=validate` flag
```bash
goreleaser release --clean --skip=validate
```
**Result**: Validation skipped successfully, but still tried to build

## Potential Root Causes

### 1. **Non-Go Project Detection**
GoReleaser detected this is not a Go module:
```
loading go mod information
  • pipe skipped or partially skipped reason=not a go module
```

However, it still attempted to build as if it were a Go project, ignoring the prebuilt configuration.

### 2. **Prebuilt Feature Requirements**
The GoReleaser Pro prebuilt feature documentation (https://goreleaser.com/customization/prebuilt/) may have undocumented requirements or assumptions:
- May require a `go.mod` file even for prebuilt binaries
- May need additional configuration flags not discovered
- Template variables in path might not be resolving correctly

### 3. **Builder Detection Logic**
Without explicitly setting `skip: true` on the build, GoReleaser's default behavior might be to attempt building:
- The `prebuilt` directive might be supplementary, not replacement
- May need both `skip: true` AND `prebuilt` configuration

### 4. **Version or Documentation Issues**
- GoReleaser Pro v2.12.5 behavior might differ from documentation
- Prebuilt feature might be experimental or have edge cases
- Rust/non-Go binary handling might not be fully supported

## Lessons Learned

1. **GoReleaser is Go-centric**: Despite "prebuilt" feature, core assumptions favor Go projects
2. **Directory structure matters**: Exact naming convention is critical (`{binary}_{os}_{arch}_v{version}`)
3. **Validation !== Build**: `--skip=validate` doesn't skip the build step
4. **Non-Go projects need extra care**: May require undocumented configuration

## Why We're Moving to nfpm

1. **Simplicity**: nfpm is purpose-built for creating Linux packages from existing binaries
2. **No magic**: Explicit configuration, no implicit build attempts
3. **Proven**: nfpm is what GoReleaser uses internally for .deb creation
4. **Control**: Direct control over packaging without fighting tooling assumptions
5. **Transparency**: Easier to debug when things go wrong

## Files Changed for This Attempt

- `.goreleaser.yml` - GoReleaser Pro configuration with prebuilt
- `.github/workflows/release-deb.yml` - Multi-stage workflow with GoReleaser Pro action
- `goreleaser-pro.md` - Documentation of intended GoReleaser Pro usage
- `scripts/postinstall.sh` - Post-installation hooks
- `scripts/preremove.sh` - Pre-removal hooks

## Future Investigation

If revisiting this approach:

1. **Contact GoReleaser Pro support** with this specific use case
2. **Try `skip: true` in builds** configuration alongside `prebuilt`
3. **Create minimal Go wrapper** that satisfies GoReleaser's expectations
4. **Use `builder: prebuilt`** if such a directive exists (not found in current docs)
5. **Check for newer GoReleaser Pro versions** with improved Rust support

## Relevant GitHub Issues / Discussions

- GoReleaser prebuilt documentation: https://goreleaser.com/customization/prebuilt/
- Error reference: https://goreleaser.com/errors/no-main
- GoReleaser Pro: https://goreleaser.com/pro/

## Conclusion

While GoReleaser Pro is an excellent tool for Go projects, its prebuilt feature for non-Go binaries (specifically Rust) proved problematic. The tool consistently attempted to build despite having pre-built binaries in the correct location.

Moving to nfpm provides a simpler, more direct path to creating .deb packages from our AlmaLinux-built Rust binaries.

This attempt was valuable for:
- Understanding GoReleaser Pro's architecture
- Learning the prebuilt feature's expectations
- Documenting a multi-stage CI/CD approach
- Creating reusable packaging hooks and scripts

The multi-stage workflow architecture (Build on AlmaLinux → Package with tool → Create Release) remains sound and will be preserved in the nfpm-based approach.
