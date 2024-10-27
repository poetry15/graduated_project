const ngrok_url = "https://5e99-125-231-4-159.ngrok-free.app"; // 請替換為實際的ngrok URL

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_NGROK_URL") {
        sendResponse({ url: ngrok_url });
    }
});