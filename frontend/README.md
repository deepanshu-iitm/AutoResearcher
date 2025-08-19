# AutoResearcher Frontend

Professional React frontend for the AutoResearcher AI research assistant.

## Features

- **Modern Dark Blue Theme**: Professional, minimal design with dark blue color scheme
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Research**: Generate comprehensive research reports with live progress
- **Knowledge Base Search**: Search through processed documents using vector similarity
- **Statistics Dashboard**: View collection stats and source breakdowns
- **Export Capabilities**: Download reports as Markdown files

## Tech Stack

- **React 18** with Vite for fast development
- **TailwindCSS** for professional styling
- **Lucide React** for beautiful icons
- **Axios** for API communication

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Make sure your backend is running**
   ```bash
   # In the main project directory
   uvicorn app.main:app --reload
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Usage

1. **Research Tab**: Enter your research goal and generate comprehensive reports
2. **Report Tab**: View generated reports with citations and download options
3. **Statistics Tab**: Explore your knowledge base and search processed documents

## API Integration

The frontend communicates with your FastAPI backend through:
- `/api/generate-report` - Generate comprehensive research reports
- `/api/stats` - Get knowledge base statistics
- `/api/search` - Search processed documents

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.
