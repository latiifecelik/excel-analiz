// Sidebar state management
let sidebarOpen = false;
let chatIcon = null;

// Debug logging function
function debugLog(message, ...args) {
    console.log('[Sidebar Debug]:', message, ...args);
}

// Initialize chat icon
function initializeChatIcon() {
    if (chatIcon) {
        debugLog('Chat icon already exists');
        return;
    }
    
    try {
        chatIcon = document.createElement('div');
        chatIcon.id = 'chat-icon';
        chatIcon.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #4a90e2;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            transition: transform 0.3s ease;
        `;
        
        chatIcon.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"></path></svg>';
        
        if (document.body) {
            document.body.appendChild(chatIcon);
            debugLog('Chat icon successfully added to document body');
            setupChatIconEvents();
            chatIcon.style.transform = 'scale(0)';
            setTimeout(() => {
                chatIcon.style.transform = 'scale(1)';
            }, 100);
        } else {
            debugLog('Document body not available');
            chatIcon = null;
        }
    } catch (error) {
        debugLog('Error initializing chat icon:', error);
        chatIcon = null;
    }
}

// Setup chat icon event listeners
function setupChatIconEvents() {
    if (!chatIcon) return;
    
    chatIcon.addEventListener('click', () => {
        try {
            window.postMessage({ type: 'toggleSidebar' }, '*');
            debugLog('Toggle sidebar event sent');
        } catch (error) {
            debugLog('Error sending toggle message:', error);
        }
    });
}

// Message listener for sidebar state changes
window.addEventListener('message', (event) => {
    const message = event.data;
    debugLog('Received message:', message);
    
    switch (message.type) {
        case 'sidebarReady':
        case 'sidebarOpen':
            debugLog('Sidebar is ready or open');
            sidebarOpen = true;
            if (chatIcon) {
                try {
                    // Improved DOM element check and removal
                    if (chatIcon instanceof Element && document.body.contains(chatIcon)) {
                        chatIcon.remove();
                        debugLog('Chat icon successfully removed');
                    } else {
                        debugLog('Chat icon is not in document body');
                    }
                } catch (error) {
                    debugLog('Error during chat icon removal:', error);
                } finally {
                    chatIcon = null;
                }
            }
            return Promise.resolve({ status: 'State Updated to Open' });
            
        case 'sidebarClosed':
            debugLog('Sidebar is closed');
            sidebarOpen = false;
            // Only initialize if chat icon doesn't exist
            if (!chatIcon) {
                initializeChatIcon();
            }
            return Promise.resolve({ status: 'State Updated to Closed' });
            
        default:
            return Promise.resolve({ status: 'Unknown message type' });
    }
});

// Storage change listener
window.addEventListener('storage', (event) => {
    if (event.key === 'isSidebarOpen') {
        debugLog('Detected change in sidebar open state:', event.newValue);
        try {
            sidebarOpen = event.newValue === 'true';
            
            if (sidebarOpen) {
                if (chatIcon instanceof Element && document.body.contains(chatIcon)) {
                    chatIcon.remove();
                    debugLog('Chat icon successfully removed');
                }
                chatIcon = null;
            } else if (!chatIcon) {
                initializeChatIcon();
            }
        } catch (error) {
            debugLog('Error handling storage event:', error);
        }
    }
});

// Initialize on page load
window.addEventListener('load', () => {
    debugLog('Page has fully loaded. Checking sidebar status...');
    
    try {
        const isSidebarOpen = localStorage.getItem('isSidebarOpen');
        sidebarOpen = isSidebarOpen === 'true';
        
        if (!sidebarOpen && !chatIcon) {
            initializeChatIcon();
        }
    } catch (error) {
        debugLog('Error during initialization:', error);
        // Only initialize if chat icon doesn't exist
        if (!chatIcon) {
            initializeChatIcon();
        }
    }
});