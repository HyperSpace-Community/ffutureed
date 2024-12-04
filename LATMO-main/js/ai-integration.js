class AIAssistant {
    constructor() {
        this.baseUrl = '/api';  // Update this with your actual API endpoint
    }

    async processQuery(query) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error processing AI query:', error);
            throw error;
        }
    }

    async searchWikipedia(query) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/wikipedia`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error searching Wikipedia:', error);
            throw error;
        }
    }

    async createGmailDraft(messageDetails) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/gmail/draft`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(messageDetails)
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating Gmail draft:', error);
            throw error;
        }
    }

    async createCalendarEvent(eventDetails) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/calendar/event`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventDetails)
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating calendar event:', error);
            throw error;
        }
    }
}

// Export the AIAssistant class
export const aiAssistant = new AIAssistant();
