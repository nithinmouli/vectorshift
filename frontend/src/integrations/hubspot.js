 import { useState, useEffect } from 'react';
import { Box, Button, CircularProgress, Typography, Alert, Chip } from '@mui/material';
import axios from 'axios';

export const HubSpotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [itemsCount, setItemsCount] = useState(null);

    const validateInputs = () => {
        if (!user || !org) {
            setError('User ID and Organization ID are required');
            return false;
        }
        return true;
    };

    const handleConnectClick = async () => {
        if (!validateInputs()) return;

        try {
            setIsConnecting(true);
            setError(null);
            
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            
            const response = await axios.post(
                'http://localhost:8000/integrations/hubspot/authorize', 
                formData,
                { timeout: 10000 }
            );
            
            const authURL = response?.data;
            if (!authURL) {
                throw new Error('No authorization URL received');
            }

            const newWindow = window.open(
                authURL, 
                'HubSpot Authorization', 
                'width=600,height=700,scrollbars=yes,resizable=yes'
            );

            if (!newWindow) {
                throw new Error('Popup blocked. Please allow popups and try again.');
            }

            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 1000);

        } catch (error) {
            console.error('Authorization error:', error);
            setIsConnecting(false);
            
            let errorMessage = 'Failed to start authorization';
            if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            setError(errorMessage);
        }
    };

    const handleWindowClosed = async () => {
        try {
            setIsLoading(true);
            
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            
            const response = await axios.post(
                'http://localhost:8000/integrations/hubspot/credentials', 
                formData,
                { timeout: 10000 }
            );
            
            const credentials = response.data;
            if (credentials && credentials.access_token) {
                setIsConnected(true);
                setIntegrationParams(prev => ({ 
                    ...prev, 
                    credentials: credentials, 
                    type: 'HubSpot' 
                }));
                
                console.log('HubSpot connected successfully!');
                
                await testIntegrationConnection(credentials);
            } else {
                throw new Error('Invalid credentials received');
            }
            
        } catch (error) {
            console.error('Credential retrieval error:', error);
            
            let errorMessage = 'Failed to complete authorization';
            if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            setError(errorMessage);
            
        } finally {
            setIsConnecting(false);
            setIsLoading(false);
        }
    };

    const testIntegrationConnection = async (credentials) => {
        try {
            console.log('Testing HubSpot integration by fetching data...');
            
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            
            const response = await axios.post(
                'http://localhost:8000/integrations/hubspot/get_hubspot_items', 
                formData,
                { timeout: 30000 }
            );
            
            const items = response.data || [];
            setItemsCount(items.length);
            
            console.log(`Successfully fetched ${items.length} items from HubSpot:`, items);
            
            const summary = items.reduce((acc, item) => {
                acc[item.type] = (acc[item.type] || 0) + 1;
                return acc;
            }, {});
            
            console.log('HubSpot Items Summary:', summary);
            
        } catch (error) {
            console.error('Failed to fetch HubSpot items:', error);
            setError('Connected but failed to fetch data. Check console for details.');
        }
    };

    const handleDisconnect = () => {
        setIsConnected(false);
        setIntegrationParams(prev => ({ 
            ...prev, 
            credentials: null, 
            type: null 
        }));
        setItemsCount(null);
        setError(null);
    };

    useEffect(() => {
        const hasCredentials = integrationParams?.credentials?.access_token;
        setIsConnected(Boolean(hasCredentials));
        
        if (hasCredentials && !itemsCount) {
            testIntegrationConnection(integrationParams.credentials);
        }
    }, [integrationParams]);

    const getButtonText = () => {
        if (isConnecting) return 'Connecting...';
        if (isLoading) return 'Loading...';
        if (isConnected) return 'HubSpot Connected';
        return 'Connect to HubSpot';
    };

    const getButtonColor = () => {
        if (error) return 'error';
        if (isConnected) return 'success';
        return 'primary';
    };

    return (
        <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>
                HubSpot Integration
            </Typography>
            
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}
            
            <Box display="flex" alignItems="center" justifyContent="center" gap={2} sx={{ mt: 2 }}>
                <Button 
                    variant="contained" 
                    onClick={isConnected ? handleDisconnect : handleConnectClick}
                    color={getButtonColor()}
                    disabled={isConnecting || isLoading}
                    size="large"
                >
                    {(isConnecting || isLoading) ? (
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                    ) : null}
                    {getButtonText()}
                </Button>
                
                {isConnected && itemsCount !== null && (
                    <Chip 
                        label={`${itemsCount} items loaded`}
                        color="success"
                        variant="outlined"
                    />
                )}
            </Box>
            
            {isConnected && (
                <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
                        Integration active. Data will be available in the console.
                    </Typography>
                </Box>
            )}
        </Box>
    );
};
