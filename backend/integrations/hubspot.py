# hubspot.py

import datetime
import json
import secrets
import logging
from typing import List, Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
from urllib.parse import urlencode
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from config import config
logger = logging.getLogger(__name__)

HUBSPOT_AUTH_URL = 'https://app.hubspot.com/oauth/authorize'
HUBSPOT_TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
HUBSPOT_API_BASE = 'https://api.hubapi.com'
SCOPES = 'crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read'
def validate_config() -> None:
    if not config.validate_hubspot_config():
        raise HTTPException(
            status_code=500, 
            detail=" Please set environment variables."
        )

async def authorize_hubspot(user_id: str, org_id: str) -> str:
    validate_config()
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    params = {
        'client_id': config.HUBSPOT_CLIENT_ID,
        'redirect_uri': config.HUBSPOT_REDIRECT_URI,
        'scope': SCOPES,
        'response_type': 'code',
        'state': encoded_state
    }
    auth_url = f'{HUBSPOT_AUTH_URL}?{urlencode(params)}'
    await add_key_value_redis(
        f'hubspot_state:{org_id}:{user_id}', 
        json.dumps(state_data), 
        expire=600
    )
    logger.info(f"Generated HubSpot auth URL for user {user_id} in org {org_id}")
    return auth_url
async def oauth2callback_hubspot(request: Request) -> HTMLResponse:
    validate_config()

    if request.query_params.get('error'):
        error_desc = request.query_params.get('error_description', 'Unknown OAuth error')
        logger.error(f"HubSpot OAuth error: {error_desc}")
        raise HTTPException(status_code=400, detail=error_desc)
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    if not code or not encoded_state:
        raise HTTPException(status_code=400, detail='Missing authorization code or state parameter')
    try:
        state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))
        original_state = state_data.get('state')
        user_id = state_data.get('user_id')
        org_id = state_data.get('org_id') 
        if not all([original_state, user_id, org_id]):
            raise ValueError("Missing required state data") 
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid state parameter: {e}")
        raise HTTPException(status_code=400, detail='Invalid state parameter')
    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state:
        raise HTTPException(status_code=400, detail='State not found or expired')
    try:
        saved_state_data = json.loads(saved_state)
        if original_state != saved_state_data.get('state'):
            raise HTTPException(status_code=400, detail='State verification failed')
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid saved state data')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.HUBSPOT_REDIRECT_URI,
        'client_id': config.HUBSPOT_CLIENT_ID,
        'client_secret': config.HUBSPOT_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                HUBSPOT_TOKEN_URL,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30.0
            )
            response.raise_for_status()  
        except httpx.HTTPStatusError as e:
            logger.error(f"HubSpot token exchange failed: {e.response.text}")
            raise HTTPException(status_code=400, detail='Failed to exchange authorization code for access token')
        except httpx.RequestError as e:
            logger.error(f"Request error during token exchange: {e}")
            raise HTTPException(status_code=500, detail='Network error during token exchange')
    credentials = response.json()
    credentials['retrieved_at'] = datetime.datetime.utcnow().isoformat()
    await asyncio.gather(
        add_key_value_redis(
            f'hubspot_credentials:{org_id}:{user_id}', 
            json.dumps(credentials), 
            expire=3600
        ),
        delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
    )
    logger.info(f"Successfully stored HubSpot  for user {user_id} in org {org_id}")
    return HTMLResponse(content="""
    <html>
        <head><title>Authorization Complete</title></head>
        <body>
            <script>
                window.close();
            </script>
            <p>Authorization successful! You can close this window.</p>
        </body>
    </html>
    """)
async def get_hubspot_credentials(user_id: str, org_id: str) -> Dict[str, Any]:
    credentials_data = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials_data:
        raise HTTPException(
            status_code=400, 
            detail='No HubSpot credentials found. Please authorize the integration first.'
        )
    try:
        credentials = json.loads(credentials_data)
        logger.info(f"Retrieved HubSpot credentials for user {user_id} in org {org_id}")
        return credentials
    except json.JSONDecodeError:
        logger.error(f"Invalid credentials data for user {user_id} in org {org_id}")
        await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
        raise HTTPException(status_code=400, detail='Invalid credentials data')
async def create_integration_item_from_contact(contact_data: Dict[str, Any]) -> IntegrationItem:
    properties = contact_data.get('properties', {})
    contact_id = contact_data.get('id')
    first_name = properties.get('firstname', '').strip()
    last_name = properties.get('lastname', '').strip()
    name = f"{first_name} {last_name}".strip() or 'Unnamed Contact'
    created_at = None
    updated_at = None
    if properties.get('createdate'):
        try:
            created_at = datetime.datetime.fromisoformat(
                properties['createdate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    if properties.get('lastmodifieddate'):
        try:
            updated_at = datetime.datetime.fromisoformat(
                properties['lastmodifieddate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    return IntegrationItem(
        id=contact_id,
        type='contact',
        name=name,
        creation_time=created_at,
        last_modified_time=updated_at,
        url=f"https://app.hubspot.com/contacts/{contact_id}" if contact_id else None,
        parent_path_or_name=properties.get('email', 'No email provided'),
        visibility=True
    )
async def create_integration_item_from_company(company_data: Dict[str, Any]) -> IntegrationItem:
    properties = company_data.get('properties', {})
    company_id = company_data.get('id')
    name = properties.get('name', 'Unnamed Company')
    domain = properties.get('domain', 'No domain')
    created_at = None
    updated_at = None
    if properties.get('createdate'):
        try:
            created_at = datetime.datetime.fromisoformat(
                properties['createdate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    if properties.get('hs_lastmodifieddate'):
        try:
            updated_at = datetime.datetime.fromisoformat(
                properties['hs_lastmodifieddate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    return IntegrationItem(
        id=company_id,
        type='company',
        name=name,
        creation_time=created_at,
        last_modified_time=updated_at,
        url=f"https://app.hubspot.com/companies/{company_id}" if company_id else None,
        parent_path_or_name=domain,
        visibility=True
    )
async def create_integration_item_from_deal(deal_data: Dict[str, Any]) -> IntegrationItem:
    properties = deal_data.get('properties', {})
    deal_id = deal_data.get('id')
    name = properties.get('dealname', 'Unnamed Deal')
    amount = properties.get('amount', '0')
    stage = properties.get('dealstage', 'Unknown Stage')
    created_at = None
    updated_at = None
    if properties.get('createdate'):
        try:
            created_at = datetime.datetime.fromisoformat(
                properties['createdate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    if properties.get('hs_lastmodifieddate'):
        try:
            updated_at = datetime.datetime.fromisoformat(
                properties['hs_lastmodifieddate'].replace('Z', '+00:00')
            )
        except (ValueError, TypeError):
            pass
    return IntegrationItem(
        id=deal_id,
        type='deal',
        name=f"{name} (${amount})",
        creation_time=created_at,
        last_modified_time=updated_at,
        url=f"https://app.hubspot.com/deals/{deal_id}" if deal_id else None,
        parent_path_or_name=stage,
        visibility=True
    )
async def fetch_hubspot_data(access_token: str, endpoint: str, properties: List[str]) -> List[Dict[str, Any]]:
    all_results = []
    after = None
    async with httpx.AsyncClient() as client:
        while True:
            params = {
                'limit': 100,
                'properties': ','.join(properties)
            }
            if after:
                params['after'] = after
            try:
                response = await client.get(
                    f"{HUBSPOT_API_BASE}/{endpoint}",
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json',
                    },
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"HubSpot API error for {endpoint}: {e.response.text}")
                if e.response.status_code == 401:
                    raise HTTPException(status_code=401, detail='HubSpot access token expired. Please re-authorize.')
                raise HTTPException(status_code=400, detail=f'Failed to fetch data from HubSpot: {e.response.text}')
                
            except httpx.RequestError as e:
                logger.error(f"Request error for {endpoint}: {e}")
                raise HTTPException(status_code=500, detail='Network error while fetching HubSpot data')
            data = response.json()
            results = data.get('results', [])
            all_results.extend(results)
            paging = data.get('paging', {})
            after = paging.get('next', {}).get('after')
            if not after:
                break
    return all_results
async def get_items_hubspot(credentials: Dict[str, Any]) -> List[IntegrationItem]:
    access_token = credentials.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail='No access token found in credentials')
    integration_items = []
    try:
        logger.info("Fetching HubSpot contacts...")
        contact_properties = ['firstname', 'lastname', 'email', 'createdate', 'lastmodifieddate']
        contacts = await fetch_hubspot_data(access_token, 'crm/v3/objects/contacts', contact_properties)
        for contact in contacts:
            item = await create_integration_item_from_contact(contact)
            integration_items.append(item)
        logger.info(f"Fetched {len(contacts)} contacts from HubSpot")
        logger.info("Fetching HubSpot companies...")
        company_properties = ['name', 'domain', 'createdate', 'hs_lastmodifieddate']
        companies = await fetch_hubspot_data(access_token, 'crm/v3/objects/companies', company_properties)
        for company in companies:
            item = await create_integration_item_from_company(company)
            integration_items.append(item)
        logger.info(f"Fetched {len(companies)} companies from HubSpot")
        logger.info("Fetching HubSpot deals...")
        deal_properties = ['dealname', 'amount', 'dealstage', 'createdate', 'hs_lastmodifieddate']
        deals = await fetch_hubspot_data(access_token, 'crm/v3/objects/deals', deal_properties)
        for deal in deals:
            item = await create_integration_item_from_deal(deal)
            integration_items.append(item)
        logger.info(f"Fetched {len(deals)} deals from HubSpot")
    except Exception as e:
        logger.error(f"Error fetching HubSpot data: {e}")
        raise
    total_items = len(integration_items)
    contacts_count = len([item for item in integration_items if item.type == 'contact'])
    companies_count = len([item for item in integration_items if item.type == 'company'])
    deals_count = len([item for item in integration_items if item.type == 'deal'])
    print(f"\n=== HubSpot Integration Items Summary ===")
    print(f"Total Items: {total_items}")
    print(f"Contacts: {contacts_count}")
    print(f"Companies: {companies_count}")
    print(f"Deals: {deals_count}")
    print(f"========================================\n")
    for item in integration_items[:10]:
        print(f"- {item.type.upper()}: {item.name} ({item.parent_path_or_name})")
    if total_items > 10:
        print(f"... and {total_items - 10} more items")
    logger.info(f"Successfully processed {total_items} HubSpot integration items")
    return integration_items