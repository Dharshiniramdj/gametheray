# Focus Catcher - Visual Attention Game

## Overview

Focus Catcher is a visual attention game built with React and TypeScript, designed to improve focus and impulse control. The application features a full-stack architecture with Express.js backend and React frontend, using PostgreSQL for data persistence and Drizzle ORM for database operations.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand for global state management
- **UI Components**: Radix UI components with Tailwind CSS for styling
- **3D Graphics**: React Three Fiber for 3D rendering capabilities
- **Data Fetching**: TanStack Query for server state management
- **Build Tool**: Vite for development and production builds

### Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **API Design**: RESTful endpoints under `/api` prefix
- **Middleware**: Custom logging and error handling middleware
- **Development**: Vite integration for hot module replacement in development

### Database Layer
- **Database**: PostgreSQL (configured via Drizzle)
- **ORM**: Drizzle ORM with schema-first approach
- **Connection**: Neon Database serverless connection
- **Migrations**: Managed through Drizzle Kit

## Key Components

### Game Engine
- **Core**: Custom game engine (`GameEngine.ts`) managing game objects and interactions
- **Objects**: Factory pattern for creating game objects with different types (stars, balloons, hearts, etc.)
- **Levels**: Configurable level system with progressive difficulty
- **Audio**: Web Audio API integration for sound effects and background music

### User Interface
- **Game States**: Menu, level selection, gameplay, and progress tracking
- **Responsive Design**: Mobile-first approach with touch support
- **Component Library**: Comprehensive UI component system using Radix primitives
- **Styling**: Tailwind CSS with custom design tokens and dark mode support

### State Management
- **Game State**: Zustand stores for game logic, audio, and user progress
- **Persistence**: Local storage for user progress and settings
- **Session Tracking**: Detailed analytics for gameplay sessions and performance metrics

## Data Flow

1. **User Authentication**: Basic user schema with username/password (ready for expansion)
2. **Game Progress**: Local storage persistence with session tracking
3. **Performance Analytics**: Reaction time measurements and accuracy tracking
4. **Level Progression**: Unlock system based on performance thresholds
5. **Audio Management**: Centralized audio state with mute/unmute functionality

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: PostgreSQL connection for serverless environments
- **drizzle-orm**: Type-safe database queries and migrations
- **@tanstack/react-query**: Server state management and caching
- **zustand**: Lightweight state management
- **@radix-ui/***: Accessible UI component primitives
- **@react-three/fiber**: 3D rendering capabilities

### Development Tools
- **tsx**: TypeScript execution for development
- **esbuild**: Fast bundling for production
- **tailwindcss**: Utility-first CSS framework
- **vite**: Build tool and development server

## Deployment Strategy

### Development Environment
- **Dev Server**: Vite development server with HMR
- **Database**: Drizzle push for schema synchronization
- **Type Checking**: Continuous TypeScript compilation checking

### Production Build
- **Frontend**: Vite build targeting `dist/public`
- **Backend**: esbuild bundling to `dist/index.js`
- **Static Assets**: Support for GLTF models and audio files
- **Environment**: NODE_ENV-based configuration

### Database Management
- **Schema**: Centralized schema definition in `shared/schema.ts`
- **Migrations**: Generated in `./migrations` directory
- **Connection**: Environment variable-based DATABASE_URL configuration

## Changelog

```
Changelog:
- July 01, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```