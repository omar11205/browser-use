import requests


def run_agent():
	url = 'http://localhost:8000/run'
	headers = {'Content-Type': 'application/json'}
	payload = {
		'task': 'Search for the today weather in New York City.',
		'model': 'gpt-4o',
		'initial_actions': [{'open_tab': {'url': 'https://www.bing.com'}}],
		'browser_context_config': {
			'locale': 'en-US',
			'minimum_wait_page_load_time': 0.5,
			'wait_for_network_idle_page_load_time': 1.0,
			'maximum_wait_page_load_time': 5.0,
			'allowed_domains': ['bing.com', 'yahoo.com'],
			'viewport_expansion': 500,
		},
		'return_screenshots': False,
		'callback_url': 'http://localhost:8888/callback',
	}

	# Send POST with JSON payload (requests adds the correct Content-Type header automatically) :contentReference[oaicite:0]{index=0}
	response = requests.post(url, json=payload, headers=headers)

	# Print status and response body :contentReference[oaicite:1]{index=1}
	print(f'Status Code: {response.status_code}')
	print('Response Body:')
	print(response.text)


if __name__ == '__main__':
	run_agent()
