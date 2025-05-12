import asyncio  # noqa: I001
import time
import os
import json
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig
import logging

logger = logging.getLogger(__name__)


async def test_process_dom():
	config = BrowserContextConfig(
		cookies_file='cookies_zoho.js',
		disable_security=True,
		wait_for_network_idle_page_load_time=20000,
	)

	browser = Browser(
		config=BrowserConfig(headless=True, browser_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
	)

	context = BrowserContext(browser=browser, config=config)

	async with context as context:
		page = await context.get_current_page()
		await page.goto('https://people.zoho.com/')

		time.sleep(3)

		with open('D:/GIT/browser_use/browser-use/browser_use/dom/buildDomTree.js', 'r') as f:
			js_code = f.read()

		args = {
			'doHighlightElements': True,
			'focusHighlightIndex': -1,
			'viewportExpansion': 0,
			'debugMode': False,
		}

		try:
			# start = time.time()
			dom_tree = await page.evaluate(js_code, args)
		except Exception as e:
			logger.error('Error evaluating Javascript: %s', e)
			raise
			# end = time.time()

		# print(dom_tree)
		# print(f'Time: {end - start:.2f}s')

		os.makedirs('./tmp', exist_ok=True)
		with open('./tmp/dom.json', 'w') as f:
			json.dump(dom_tree, f, indent=1)

		# both of these work for immobilienscout24.de
		# await page.click('.sc-dcJsrY.ezjNCe')
		# await page.click(
		# 	'div > div:nth-of-type(2) > div > div:nth-of-type(2) > div > div:nth-of-type(2) > div > div > div > button:nth-of-type(2)'
		# )
		print('dom tree ready')
		# test screenshot
		# await page.click()
		await page.screenshot(path='D:/GIT/browser_use/browser-use/browser_use/dom/tests/screenshot.png')
		print('screenshotready')
		input('Press Enter to continue...')


if __name__ == '__main__':
	# asyncio.run(test_focus_vs_all_elements())
	asyncio.run(test_process_dom())
