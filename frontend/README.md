# LandGuard & PCC Frontend

Modern web interface for the LandGuard & PCC secure document processing platform.

## Features

- **Responsive Design**: Works on all device sizes
- **Interactive UI**: Smooth animations and transitions
- **Feature Showcase**: Highlights all core LandGuard & PCC capabilities
- **Technology Display**: Shows the tech stack powering the platform
- **Demo Access**: Easy access to try the platform

## Technology Stack

- **React**: Modern component-based UI library
- **Vite**: Ultra-fast development server and build tool
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Framer Motion**: Production-ready motion library for React
- **Lucide React**: Beautiful SVG icons as React components

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/compression-.git
cd compression-/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open your browser to `http://localhost:5173`

### Building for Production

To create a production build:

```bash
npm run build
# or
yarn build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
├── components/
│   ├── ui/          # Reusable UI components
│   └── layout/      # Page layout components
├── App.jsx          # Main application component
├── main.jsx         # Application entry point
└── assets/          # Static assets (images, fonts, etc.)
```

## Key Components

### Landing Page
Showcases the main features of LandGuard & PCC:
- AI-powered fraud detection
- Military-grade encryption
- Intelligent compression
- Decentralized storage
- Blockchain verification
- Secure packaging

### Feature Sections
- **Hero Section**: Eye-catching introduction with CTAs
- **Features Grid**: Highlighting core capabilities
- **Workflow Visualization**: Step-by-step process explanation
- **Technology Stack**: Display of underlying technologies
- **Call to Action**: Conversion-focused section

## Customization

To customize the website:

1. Modify `src/App.jsx` to change content and structure
2. Update styles in Tailwind classes directly in JSX
3. Add new components in `src/components/`
4. Modify color scheme in `tailwind.config.js`

## Deployment

The site can be deployed to any static hosting service:

- Vercel (recommended)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Firebase Hosting

### Deploy to Vercel

1. Push your code to GitHub
2. Sign up/in to Vercel
3. Import your repository
4. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Deploy!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary software for the LandGuard & PCC platform.

## Support

For support, contact the development team or check the main project documentation.