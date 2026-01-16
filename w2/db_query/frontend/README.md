# DB Query Frontend

Natural Language SQL Explorer - Frontend Application

## Description

React-based frontend for the DB Query tool that provides an intuitive web interface for connecting to PostgreSQL databases, exploring schema metadata, executing SQL queries, and generating SQL from natural language.

## Features

- Database connection management with visual interface
- Schema browser showing tables, views, and columns
- Monaco Editor for SQL query editing
- Natural language query input
- Query results display in tabular format
- Query history tracking

## Requirements

- Node.js 18+
- npm or yarn package manager

## Installation

```bash
npm install
```

## Configuration

The frontend connects to the backend API. By default, it expects the backend to be running at `http://localhost:8000`.

To configure a different API URL, set the environment variable:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Running

### Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Development

### Type Checking

```bash
npm run typecheck
```

### Linting

```bash
npm run lint
```

## Technology Stack

- **React 18**: UI framework
- **Refine 5**: Data provider and routing
- **Ant Design 5**: Component library
- **Monaco Editor**: SQL code editor
- **Tailwind CSS**: Styling
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/        # API service layer
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## API Integration

The frontend communicates with the backend API at `/api/v1`. All API calls are handled through the service layer in `src/services/api.ts`.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
