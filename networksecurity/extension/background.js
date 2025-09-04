const API_URL = "http://127.0.0.1:8000/check-batch-link";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SCRAPED_LINKS") {
    console.log("Links received:", message.links);

    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.links) // send whole list
    })
    .then(res => res.json())
    .then(data => {
      console.log("Results:", data);
      chrome.storage.local.set(data); // save all results
    })
    .catch(err => console.error("Error checking links:", err));
  }
});
