// Main JavaScript for TaskFlowAI

// Utility functions
const TaskFlowAI = {
    api: {
        async get(url) {
            const response = await fetch(url);
            return response.json();
        },
        
        async post(url, data) {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.json();
        },
        
        async put(url, data) {
            const response = await fetch(url, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return response.json();
        },
        
        async delete(url) {
            const response = await fetch(url, { method: 'DELETE' });
            return response.json();
        }
    },
    
    showNotification(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = 9999;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaskFlowAI;
}
