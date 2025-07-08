# SnapTrace Website

This folder contains the professional website for SnapTrace 2.0.

## Files Structure

```
www/
├── index.html          # Main website page
├── css/
│   └── style.css       # Website styles
├── js/
│   └── script.js       # Interactive functionality
└── images/
    ├── og-image.png    # Open Graph image for social sharing
    └── screenshots/    # Application screenshots
        ├── hero-screenshot.png
        ├── main-interface.png
        ├── drawing-tools.png
        ├── system-tray.png
        ├── text-annotation.png
        └── defect-templates.png
```

## Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional appearance with gradient backgrounds
- **Interactive Gallery**: Click any screenshot to view in full-screen modal
- **Smooth Scrolling**: Navigation links smoothly scroll to sections
- **SEO Optimized**: Meta tags, Open Graph, and Twitter Card support
- **Performance**: Lightweight with optimized images and minimal dependencies

## Customization

### Updating Screenshots

Replace the placeholder images in `images/screenshots/` with actual application screenshots:

1. `hero-screenshot.png` - Main hero image (800x500px)
2. `main-interface.png` - Application interface (600x400px)
3. `drawing-tools.png` - Drawing tools in action (600x400px)
4. `system-tray.png` - System tray integration (600x400px)
5. `text-annotation.png` - Text annotation features (600x400px)
6. `defect-templates.png` - Defect feedback templates (600x400px)

### Updating Links

Update the GitHub repository links in `index.html`:
- Replace `yourusername` with your actual GitHub username
- Update download links to point to your releases page

### Deployment

#### GitHub Pages
1. Push to your GitHub repository
2. Go to repository Settings > Pages
3. Select source branch (usually `main`)
4. Your site will be available at `https://yourusername.github.io/SnapTrace/www/`

#### Alternative Hosting
- Upload the `www` folder contents to any web hosting service
- Ensure `index.html` is in the root directory

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Dependencies

- Font Awesome 6.4.0 (CDN)
- Google Fonts - Inter (CDN)
- No build process required

## License

Same as the main SnapTrace project.
