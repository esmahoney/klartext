# KlarText Browser Extension (Optional Track)

This directory will contain the Chrome/Firefox extension that allows users to simplify text directly on any webpage.

## Planned Features

- Right-click context menu: "Simplify selected text"
- Toolbar button to simplify entire page content
- Settings for preferred difficulty level
- Local storage for user preferences

## Status

⏳ **Not yet implemented** – This is a stretch goal for the MVP.

## Getting Started (Future)

1. Load the extension in Chrome:
   - Go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select this directory

2. The extension will connect to the KlarText API at the configured URL.

## Structure (Planned)

```
extension/
├── manifest.json       # Extension manifest (V3)
├── popup/              # Toolbar popup UI
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── content/            # Content scripts
│   └── content.js
├── background/         # Service worker
│   └── service-worker.js
├── icons/              # Extension icons
└── README.md
```

