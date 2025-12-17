# LandGuard & PCC Frontend Setup Guide

This guide will help you set up and run the LandGuard & PCC frontend application.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Node.js** (version 16 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **npm** (comes with Node.js) or **yarn**
   - Verify npm: `npm --version`
   - Install yarn (optional): `npm install -g yarn`

## Installation Steps

### 1. Navigate to the Frontend Directory

Open your terminal/command prompt and navigate to the frontend directory:

```bash
cd f:\shivani\VSCode\projects\compression\compression-\frontend
```

### 2. Install Dependencies

Install all required packages:

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

This will install all dependencies listed in `package.json`, including:
- React and React DOM
- Framer Motion for animations
- Lucide React for icons
- Tailwind CSS for styling
- Class Variance Authority for component variants
- CLSX and Tailwind Merge for utility class management

### 3. Development Server

Start the development server:

```bash
# Using npm
npm run dev

# Or using yarn
yarn dev
```

The application will be available at `http://localhost:5173`

### 4. Building for Production

To create a production build:

```bash
# Using npm
npm run build

# Or using yarn
yarn build
```

The built files will be in the `dist/` directory.

### 5. Preview Production Build

To preview the production build locally:

```bash
# Using npm
npm run preview

# Or using yarn
yarn preview
```

## Project Structure

```
frontend/
├── index.html              # Main HTML file
├── package.json            # Project dependencies and scripts
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── src/
│   ├── main.jsx            # Application entry point
│   ├── App.jsx             # Main application component
│   ├── index.css           # Global CSS styles
│   ├── lib/
│   │   └── utils.js        # Utility functions
│   └── components/
│       ├── ui/             # Reusable UI components
│       │   ├── button.jsx
│       │   ├── card.jsx
│       │   └── badge.jsx
│       └── layout/         # Layout components
└── dist/                   # Production build output (created after build)
```

## Key Features Implemented

### 1. Responsive Design
- Mobile-first approach
- Works on all device sizes
- Adaptive layouts

### 2. Modern UI Components
- Animated buttons with variants
- Interactive cards with hover effects
- Badges for status indicators
- Consistent design system

### 3. Performance Optimized
- Fast loading with Vite
- Tree-shaking for unused code
- Optimized builds

### 4. Accessibility
- Semantic HTML
- Proper focus management
- Keyboard navigation support

## Customization

### Changing Colors
Modify the color palette in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: "hsl(var(--primary))",
        foreground: "hsl(var(--primary-foreground))",
      },
      // Add custom colors here
    }
  }
}
```

### Adding New Components
1. Create a new component file in `src/components/ui/`
2. Follow the pattern of existing components
3. Export the component in the appropriate index file

### Modifying Content
Edit `src/App.jsx` to change:
- Hero section text
- Feature descriptions
- Workflow steps
- Technology stack information

## Troubleshooting

### Common Issues

1. **Dependency Installation Failures**
   ```bash
   # Clear cache and reinstall
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Port Already in Use**
   Change the port in `vite.config.js`:
   ```javascript
   export default defineConfig({
     server: {
       port: 3000  // Change to desired port
     }
   })
   ```

3. **Build Errors**
   Check for syntax errors in JSX files
   Ensure all components are properly imported

### Browser Compatibility

The application is compatible with:
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Deployment

### Vercel (Recommended)
1. Push code to GitHub/GitLab
2. Import project in Vercel
3. Set build command: `npm run build`
4. Set output directory: `dist`

### Other Platforms
- **Netlify**: Import repository and set build settings
- **GitHub Pages**: Use gh-pages package
- **AWS S3**: Upload dist folder to bucket
- **Firebase**: Use Firebase hosting

## Development Workflow

1. **Branch Strategy**
   - Create feature branches from main
   - Submit pull requests for review
   - Merge after approval

2. **Component Development**
   - Create components in isolation
   - Use Storybook for component testing (optional)
   - Follow established patterns

3. **Styling**
   - Use Tailwind classes directly in JSX
   - Maintain consistent spacing and typography
   - Use the defined color palette

## Support

For issues with the frontend setup:
1. Check console for error messages
2. Verify all dependencies are installed
3. Ensure Node.js version is 16 or higher
4. Contact the development team for assistance

## Next Steps

After setting up the frontend:
1. Connect to backend APIs (if available)
2. Implement authentication flows
3. Add form validation
4. Integrate analytics
5. Set up CI/CD pipeline