document.addEventListener('DOMContentLoaded', () => {
    const importBtn = document.getElementById('importBtn');
    const statusText = document.getElementById('statusText');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    let currentTaskId = importBtn?.dataset.taskId || null;

    function updateUI(status) {
        const states = {
            'PENDING': { btnText: 'Importing...', infoText: 'Import in progress...', isDisabled: true },
            'SUCCESS': { btnText: 'Success', infoText: 'Import completed.', isDisabled: true },
            'FAILED':  { btnText: 'Retry', infoText: 'Import Error.', isDisabled: false }
        };

        const defaultState = { btnText: 'Sync Steam', infoText: '', isDisabled: false };
        const currentState = states[status] || defaultState;
        
        if (importBtn) {
            importBtn.disabled = currentState.isDisabled;
            importBtn.innerText = currentState.btnText;
        }

        if (statusText) {
            statusText.innerText = currentState.infoText;
        }

        if (status === 'PENDING' && currentTaskId) {
            setTimeout(() => checkStatus(currentTaskId), 3000); 
        }

        if (status === 'SUCCESS') {
            setTimeout(() => window.location.reload(), 1500);
        }
    }

    async function checkStatus(taskId) {
        if (!taskId) return;

        const checkUrl = `/games/import-status/${taskId}/`;

        try {
            const response = await fetch(checkUrl);
            const data = await response.json();
            
            updateUI(data.status);
        } catch (error) {
            console.error('Checking import status error:', error);
        }
    }

    if (currentTaskId) {
        updateUI('PENDING');
        checkStatus(currentTaskId);
    }

    importBtn?.addEventListener('click', async () => {
        updateUI('PENDING');

        try {
            const response = await fetch('/games/import-start/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            
            if (data.task_id) {
                currentTaskId = data.task_id;
                checkStatus(currentTaskId);
            } else {
                updateUI('FAILED');
                statusText.innerText = 'Error: server did not return task id.';
            }
        } catch (error) {
            updateUI('FAILED');
            statusText.innerText = 'Network error.';
        }
    });
});