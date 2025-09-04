// Collect all links on the page
function scrapeLinks() {
  let links = Array.from(document.querySelectorAll("a"))
                   .map(a => a.href)
                   .filter(href => href.startsWith("http"));

  // Include current page URL itself
  links.push(window.location.href);

  return [...new Set(links)]; // remove duplicates
}

// Send links to background
chrome.runtime.sendMessage({ type: "SCRAPED_LINKS", links: scrapeLinks() });
