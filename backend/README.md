# Backend API

FastAPI-based backend server for VectorShift integrations assessment.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Create a `.env` file with your integration credentials:
   ```
   # HubSpot
   HUBSPOT_CLIENT_ID=your_hubspot_client_id
   HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret
   
   # Airtable (if configured)
   AIRTABLE_CLIENT_ID=your_airtable_client_id
   AIRTABLE_CLIENT_SECRET=your_airtable_client_secret
   
   # Notion (if configured)
   NOTION_CLIENT_ID=your_notion_client_id
   NOTION_CLIENT_SECRET=your_notion_client_secret
   ```

3. **Start Redis server (required for session management):**
   ```bash
   redis-server
   ```

4. **Run the development server:**
   ```bash
   python main.py
   ```
   
   The server will start at `http://localhost:8000`

## API Endpoints

### HubSpot Integration
- `POST /integrations/hubspot/authorize` - Start OAuth flow
- `GET /integrations/hubspot/oauth2callback` - OAuth callback
- `POST /integrations/hubspot/credentials` - Get stored credentials
- `POST /integrations/hubspot/get_hubspot_items` - Fetch HubSpot data

### Airtable Integration
- `POST /integrations/airtable/authorize` - Start OAuth flow
- `GET /integrations/airtable/oauth2callback` - OAuth callback
- `POST /integrations/airtable/credentials` - Get stored credentials
- `POST /integrations/airtable/load` - Fetch Airtable data

### Notion Integration
- `POST /integrations/notion/authorize` - Start OAuth flow
- `GET /integrations/notion/oauth2callback` - OAuth callback
- `POST /integrations/notion/credentials` - Get stored credentials
- `POST /integrations/notion/load` - Fetch Notion data

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── redis_client.py      # Redis connection and utilities
├── requirements.txt     # Python dependencies
└── integrations/
    ├── __init__.py
    ├── integration_item.py  # Common data models
    ├── airtable.py         # Airtable integration
    ├── notion.py           # Notion integration
    └── hubspot.py          # HubSpot integration
```

## Dependencies

- **FastAPI** - Web framework
- **httpx** - HTTP client for API requests
- **redis** - Session and credential storage
- **python-dotenv** - Environment variable management

## Development

- The server runs with auto-reload enabled in development
- Check logs for debugging OAuth flows and API interactions
- Redis is required for storing OAuth credentials and session data
