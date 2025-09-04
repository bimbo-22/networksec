chrome.storage.local.get(null, (items) => {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "";

  for (const [url, result] of Object.entries(items)) {
    let div = document.createElement("div");
    div.textContent = `${url} → ${result.message}`;
    div.className = result.prediction === 1 ? "safe" : "malicious";
    resultsDiv.appendChild(div);
  }
});
