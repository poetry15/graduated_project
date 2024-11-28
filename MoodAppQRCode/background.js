const ngrok_url = "https://591f-111-246-96-198.ngrok-free.app"; // 請替換為實際的ngrok URL

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_NGROK_URL") {
        sendResponse({ url: ngrok_url });
    }
});