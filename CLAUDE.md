# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Rust project named `test-build-processes` - a minimal Rust binary application.

## Build and Development Commands

### Building
```bash
# Build the project in debug mode
cargo build

# Build the project in release mode (optimized)
cargo build --release
```

### Running
```bash
# Run the project in debug mode
cargo run

# Run the project in release mode
cargo run --release
```

### Testing
```bash
# Run all tests
cargo test

# Run tests with output shown
cargo test -- --nocapture

# Run a specific test
cargo test <test_name>
```

### Other Useful Commands
```bash
# Check code without building
cargo check

# Format code
cargo fmt

# Lint code
cargo clippy

# Clean build artifacts
cargo clean
```

## Project Structure

- `src/main.rs` - Main entry point for the binary
- `Cargo.toml` - Project manifest with dependencies and metadata
- `target/` - Build output directory (gitignored)

## Architecture Notes

This is a simple Rust binary project with a single entry point. The project uses Rust edition 2024.
