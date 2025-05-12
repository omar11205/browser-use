from playwright.sync_api import sync_playwright


def get_interactive_elements(page):
	"""Finds and returns interactive elements on the page."""

	interactive_elements = page.evaluate("""
        () => {
            function isInteractiveElement(element) {
                if (!element || element.nodeType !== Node.ELEMENT_NODE) {
                    return false;
                }

                // Special handling for cookie banner elements
                const isCookieBannerElement =
                    (typeof element.closest === 'function') && (
                        element.closest('[id*="onetrust"]') ||
                        element.closest('[class*="onetrust"]') ||
                        element.closest('[data-nosnippet="true"]') ||
                        element.closest('[aria-label*="cookie"]')
                    );

                if (isCookieBannerElement) {
                    if (
                        element.tagName.toLowerCase() === 'button' ||
                        element.getAttribute('role') === 'button' ||
                        element.onclick ||
                        element.getAttribute('onclick') ||
                        (element.classList && (
                            element.classList.contains('ot-sdk-button') ||
                            element.classList.contains('accept-button') ||
                            element.classList.contains('reject-button')
                        )) ||
                        element.getAttribute('aria-label')?.toLowerCase().includes('accept') ||
                        element.getAttribute('aria-label')?.toLowerCase().includes('reject')
                    ) {
                        return true;
                    }
                }

                // General interactive elements
                const tag = element.tagName.toLowerCase();
                if (['button', 'a', 'input', 'select', 'textarea'].includes(tag)) return true;
                if (element.getAttribute('role') === 'button') return true;
                if (element.getAttribute('onclick')) return true;

                return false;
            }

            const elements = document.querySelectorAll('*');
            return Array.from(elements)
                .filter(el => isInteractiveElement(el))
                .map(el => ({
                    tag: el.tagName,
                    text: el.innerText || el.getAttribute('aria-label') || '[No text]'
                }));
        }
    """)

	return interactive_elements


def main():
	with sync_playwright() as p:
		browser = p.chromium.launch(executable_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless=False)
		page = browser.new_page()

		# Go to Google
		page.goto('https://people.zoho.com/cariai/zp#home/myspace/overview-leave', timeout=60000)

		# Wait for the page to load
		page.wait_for_timeout(30000)

		# Get interactive elements
		interactive_elements = get_interactive_elements(page)

		print(f'Found {len(interactive_elements)} interactive elements:')
		for item in interactive_elements:  # Limit to first 10 for readability
			print(f'- {item["tag"]} | {item["text"]}')

		browser.close()


if __name__ == '__main__':
	main()
