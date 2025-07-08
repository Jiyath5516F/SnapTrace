# Changelog

All notable changes to SnapTrace will be documented in this file.

## [2.0.0] - 2025-07-08 [YYYY-MM-DD]

### Added
- Complete refactor and modernization of the codebase
- System tray integration with full background operation
- Global hotkey support (Ctrl+Alt+S) for instant screenshots
- Modular architecture with organized src/ structure
- Professional drawing tools (Rectangle, Circle, Arrow, Line, Pencil, Text, Counter)
- Advanced selection and movement system for annotations
- Color picker with predefined and custom colors
- Undo/Redo functionality with 50-level history
- External CSV file for customizable defect feedback templates
- Portable executable build with PyInstaller optimization
- Comprehensive documentation and build guides

### Changed
- Replaced pandas dependency with native Python CSV module (98.5% size reduction)
- Optimized PyInstaller build from 2.8GB to ~40MB
- Moved from embedded to external CSV file for easier customization
- Improved resource path handling for both development and portable modes
- Enhanced UI responsiveness and professional styling

### Fixed
- Import path issues in PyInstaller builds
- Resource loading in both development and compiled modes
- Text tool sticky state and duplication bugs
- Drawing area coordinate system and scaling
- Memory usage optimization

### Technical Improvements
- Modular code organization (src/core, src/ui)
- Robust error handling and logging
- Professional build system with batch scripts
- Clean project structure ready for open source distribution
- Comprehensive .gitignore and documentation

## [1.x.x] - Previous Versions
- Legacy version with basic screenshot functionality
- Monolithic codebase structure
- Limited annotation tools
