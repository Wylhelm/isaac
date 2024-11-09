// Initialize all modules when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize scenario counter
    window.scenarioCounter = 1;

    // Initialize UI components
    initializeUI();
    initializeScenarioHandling();
    initializeFileUpload();
    initializeModals();

    // Load initial scenarios
    loadScenarios();

    // Add click handler for ISAAC logo video
    document.getElementById('isaacLogo').addEventListener('click', () => {
        const videoWindow = window.open('', 'ISAAC Video', 'width=800,height=600');
        videoWindow.document.write(`
            <html>
                <body style="margin:0; padding:0;">
                    <video width="100%" height="100%" controls autoplay>
                        <source src="/static/images/isaacvideo.mp4" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </body>
            </html>
        `);
        videoWindow.document.close();
    });
});

// Global utility functions
function showAlert(message) {
    alert(message);
}

// Global error handler
window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('Error: ', msg, '\nURL: ', url, '\nLine: ', lineNo, '\nColumn: ', columnNo, '\nError object: ', error);
    return false;
};

// Export functions that need to be globally accessible
window.showAlert = showAlert;
