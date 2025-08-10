# Frontend Application

React-based frontend application for VectorShift integrations assessment.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```
   
   The app will open at `http://localhost:3000`

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (one-way operation)

## Features

### Integration Management
- **User ID & Organization ID** - Input fields for identification
- **Integration Type Selection** - Dropdown to choose integration type
- **OAuth Authentication** - Secure connection flow for each integration

### Supported Integrations

#### HubSpot Integration
- OAuth 2.0 authentication flow
- Fetches contacts, companies, and deals
- Displays connection status and item counts
- Console logging for debugging

#### Airtable Integration
- OAuth 2.0 authentication flow
- Fetches bases and tables
- Connection status display

#### Notion Integration
- OAuth 2.0 authentication flow
- Fetches pages and databases
- Connection status display

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
└── src/
    ├── App.js              # Main application component
    ├── index.js            # Application entry point
    ├── index.css           # Global styles
    ├── data-form.js        # User/Org input form
    ├── integration-form.js # Integration selection and management
    └── integrations/
        ├── airtable.js     # Airtable integration component
        ├── notion.js       # Notion integration component
        ├── hubspot.js      # HubSpot integration component
        └── slack.js        # Slack integration component (placeholder)
```

## UI Components

- **Material-UI** - React component library for consistent styling
- **Form Management** - User ID and Organization ID input
- **Integration Cards** - Individual integration management
- **OAuth Popups** - Secure authentication windows
- **Status Indicators** - Connection status and data counts

## Backend Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- OAuth authorization endpoints
- Credential management
- Data fetching and display

## Development Notes

- Built with Create React App
- Uses hooks for state management
- OAuth flows handled via popup windows
- Error handling and loading states implemented
- Console logging for debugging OAuth flows
