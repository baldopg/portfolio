# Finding a way

Independent English-language wayfinding concept study for Baldomero Perdomo García's application. Fictional North Learning Centre; no employer endorsement or regulatory compliance claim.

## Preview

Open `dist/index.html` in a browser, or serve `dist` with any static HTTP server. No build step or dependencies. Google Fonts are optional; system fonts provide an offline fallback.

## Publish with Netlify

Create a Git repository in this directory, commit the files, push to your own GitHub repository and import it in Netlify. `netlify.toml` sets the publish directory to `dist`; leave the build command empty. Alternatively upload the `dist` folder through Netlify's manual deployment interface. No credentials belong in this repository.

## Features

- Two SVG floor plans with keyboard-accessible sign selection.
- Six destination routes and a four-step guided tour.
- Nine connected sign records, three sign types, live editing and revision tracking.
- Floor-filtered register, CSV export, editable SVG export and print stylesheet.
- Responsive layout and reduced-motion support.
- Honest experience, learning needs and language statement.

Edits persist for the current page session only. Destination geometry and room names are fixed; changing a sign's text does not redesign routes. The material, dimensions and floor plan are illustrative. The exports are concept documents, not approved production files. The printed study includes the currently selected floor and current register filter; select All floors for the complete register.

## Files

`dist/index.html`: content and accessible structure. `dist/style.css`: responsive and print layout. `dist/app.js`: data, floor geometry, editor and exports.
