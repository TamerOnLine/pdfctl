# 📦 Changelog

All notable changes to this project will be documented in this file.
This project follows [Semantic Versioning](https://semver.org/).

---
## [0.1.3] - 2025-10-28
### Added
- Auto port detection (automatic fallback when port is busy)
- Improved console messages (clearer app launch output)

### Changed
- Streamlit launcher now handles exceptions gracefully

### Fixed
- Prevented infinite loop when starting app multiple times

---

## [0.1.2] - 2025-10-28
### ✨ Added
- Added command-line argument `--port` for flexible Streamlit server port selection.
- Added automatic detection of the app path for cleaner execution.

### 🛠️ Changed
- Restored full Streamlit launch behavior (`os.execvp`), allowing the app to auto-open in the browser.
- Improved CLI messages and startup logs for better developer feedback.

### 🐞 Fixed
- Fixed “missing ScriptRunContext” warning when running `pdfctl-web`.
- Fixed issue where the app would not open in the browser automatically.

---

## [0.1.1] - 2025-10-28

### Added
- ✨ Added **Streamlit Web Interface** (`pdfctl-web`) for PDF merging, splitting, rotating, and extracting.
- 🔧 Added **Trusted Publishing (OIDC)** support for automatic PyPI deployment via GitHub Actions.
- 🧩 Added support for installing via `pip install pdfctl[web]`.

### Changed
- ⚙️ Improved project structure to use `src/` layout for better packaging.
- 📦 Updated `pyproject.toml` with full dependency list and script entry points.

### Fixed
- 🐞 Fixed packaging issue caused by extra folders (`out*`, `build*`) being included during build.
- ✅ Verified successful installation and web interface launch after PyPI publication.


---
## [0.1.0] - 2025-10-28
### Added
- Web UI with Streamlit (merge / split / extract / rotate).
- Command `pdfctl-web` entry point.

### Changed
- Switched to src/ layout and uv.

### Fixed
- Package discovery issue by excluding `out*`.

---


