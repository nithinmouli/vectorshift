

# VectorShift Integrations Technical Assessment

A full-stack application demonstrating OAuth integrations with various platforms including HubSpot, Airtable, and Notion.

## Project Overview

This application showcases the implementation of OAuth 2.0 authentication flows and data fetching capabilities for multiple third-party integrations, built as a technical assessment for VectorShift.

### Completed Features

- **HubSpot Integration** - Full OAuth 2.0 flow with data fetching from contacts, companies, and deals
- **Airtable Integration** - OAuth authentication and data access
- **Notion Integration** - OAuth authentication and data access
- **User Management** - User ID and Organization ID handling
- **Data Visualization** - Connection status, item counts, and console logging
- **Error Handling** - Comprehensive error states and user feedback

## Architecture

### Backend (`/backend`)
- **FastAPI** - Modern Python web framework
- **Redis** - Session and credential storage
- **httpx** - Async HTTP client for API requests
- **OAuth 2.0** - Secure authentication flows

### Frontend (`/frontend`)
- **React** - Modern JavaScript UI library
- **Material-UI** - Consistent component design system
- **Axios** - HTTP client for API communication
- **OAuth Popups** - Secure authentication windows

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Redis server

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env file with your credentials
echo "HUBSPOT_CLIENT_ID=your_client_id" > .env
echo "HUBSPOT_CLIENT_SECRET=your_client_secret" >> .env

# Start Redis
redis-server

# Start backend server
python main.py
```

Backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

## Configuration

### HubSpot Setup
1. Create a HubSpot app at [developers.hubspot.com](https://developers.hubspot.com)
2. Configure OAuth redirect URI: `http://localhost:8000/integrations/hubspot/oauth2callback`
3. Add required scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.companies.read`
   - `crm.objects.deals.read`
4. Add credentials to `backend/.env`

### Other Integrations
Similar setup process for Airtable and Notion with their respective developer portals.

## Project Structure

```
integrations_technical_assessment/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── redis_client.py        # Redis utilities
│   ├── requirements.txt       # Python dependencies
│   └── integrations/
│       ├── hubspot.py         # HubSpot OAuth & API
│       ├── airtable.py        # Airtable OAuth & API
│       ├── notion.py          # Notion OAuth & API
│       └── integration_item.py # Common data models
├── frontend/
│   ├── package.json           # Node.js dependencies
│   ├── src/
│   │   ├── App.js            # Main application
│   │   ├── data-form.js      # User input form
│   │   ├── integration-form.js # Integration management
│   │   └── integrations/
│   │       ├── hubspot.js    # HubSpot UI component
│   │       ├── airtable.js   # Airtable UI component
│   │       └── notion.js     # Notion UI component
│   └── public/
├── README.md                  # This file
├── HUBSPOT_SETUP.md          # HubSpot configuration guide
└── ASSIGNMENT_COMPLETE.md    # Assessment completion notes
```

## Security Features

- **OAuth 2.0** - Industry-standard authentication
- **State Parameters** - CSRF protection
- **Secure Token Storage** - Redis-based credential management
- **CORS Configuration** - Proper cross-origin request handling
- **Environment Variables** - Secure credential storage

## Testing

### Backend Testing
```bash
cd backend
python test_imports.py
```

### Frontend Testing
```bash
cd frontend
npm test
```

## Data Flow

1. **User Authentication** - User provides ID and Organization ID
2. **Integration Selection** - Choose integration type (HubSpot, Airtable, Notion)
3. **OAuth Flow** - Secure popup-based authentication
4. **Credential Storage** - Tokens stored in Redis with user/org keys
5. **Data Fetching** - Authenticated API requests to fetch platform data
6. **Display** - Connection status, item counts, and console logging

## Monitoring & Debugging

- **Console Logging** - Comprehensive logging throughout OAuth flows
- **Error States** - User-friendly error messages and handling
- **Connection Status** - Real-time connection state indicators
- **Data Counts** - Visual feedback on fetched item quantities

## API Documentation

Backend API is self-documenting via FastAPI. Visit `http://localhost:8000/docs` when running.

## Assessment Notes

This project demonstrates:
- Full-stack development capabilities
- OAuth 2.0 implementation expertise
- Modern web development practices
- Clean code architecture
- Comprehensive error handling
- User experience considerations

## Contributing

This is a technical assessment project. The implementation follows modern best practices and includes comprehensive documentation for evaluation purposes.

## License

This project is created for technical assessment purposes.
#
