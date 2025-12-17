# FleetFlow Logo Assets

## Available Logos

| File | Description | Use Case |
|------|-------------|----------|
| `fleetflow-logo-full.svg` | Full logo with icon + text (Spanish tagline) | Website header, marketing (ES) |
| `fleetflow-logo-en.svg` | Full logo with icon + text (English tagline) | Website header, marketing (EN) |
| `fleetflow-logo-dark.svg` | Full logo for dark backgrounds (Spanish) | Dark mode, dark backgrounds |
| `fleetflow-wordmark.svg` | Text-only logo with accent | Simple headers, footers |
| `fleetflow-icon.svg` | Icon only (circular) | App icon, social media avatar |
| `fleetflow-favicon.svg` | Small favicon (32x32) | Browser tab, bookmarks |

## Brand Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#0EA5E9` | "Fleet" text, vehicle, primary actions |
| Cyan Accent | `#06B6D4` | Gradients, highlights |
| Orange | `#F97316` | "Flow" text, CTAs, accents |
| Light Orange | `#FB923C` | Gradients, hover states |
| Dark Gray | `#1e293b` | Wheels, dark elements |
| Medium Gray | `#64748b` | Tagline text |

## Typography

- **Primary Font**: System UI stack (`system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`)
- **Logo Weight**: 700 (Bold)
- **Tagline Weight**: 400 (Regular)

## Usage Guidelines

1. **Minimum Size**: Icon should not be smaller than 32x32px
2. **Clear Space**: Maintain padding equal to the height of the "F" around the logo
3. **Background**: Use light version on light backgrounds, dark version on dark backgrounds
4. **Don't**: Stretch, rotate, or change the colors of the logo

## Converting to Other Formats

```bash
# SVG to PNG (requires Inkscape)
inkscape -w 512 -h 512 fleetflow-icon.svg -o fleetflow-icon-512.png

# SVG to ICO (requires ImageMagick)
convert fleetflow-favicon.svg -resize 32x32 favicon.ico
```
