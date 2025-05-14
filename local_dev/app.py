import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import dotenv
import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig

dotenv.load_dotenv()


# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION VIA Pydantic BaseSettings
# ──────────────────────────────────────────────────────────────────────────────
class Settings(BaseSettings):
	HOST: str = '0.0.0.0'
	PORT: int = 8000
	GEMINI_API_KEY: SecretStr
	OPENAI_API_KEY: SecretStr
	HEADLESS: bool = True
	DISABLE_SECURITY: bool = False
	model_config = SettingsConfigDict(env_file='a.env', env_file_encoding='utf-8')


settings = Settings()  # loads from environment

# ──────────────────────────────────────────────────────────────────────────────
# 2. FASTAPI + LIFESPAN FOR BROWSER LIFECYCLE
# ──────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger('browser_use_api')
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
	browser = Browser(
		config=BrowserConfig(
			headless=settings.HEADLESS,
			disable_security=settings.DISABLE_SECURITY,
			browser_binary_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
		)
	)
	app.state.browser = browser
	logger.info('Playwright browser launched')
	try:
		yield
	finally:
		await app.state.browser.close()
		logger.info('Playwright browser closed')


app = FastAPI(
	title='Browser Use API', description='Run browser automation tasks via browser-use', version='1.0', lifespan=lifespan
)


# ──────────────────────────────────────────────────────────────────────────────
# 3. REQUEST & RESPONSE MODELS (with callback_url)
# ──────────────────────────────────────────────────────────────────────────────
class AgentRequest(BaseSettings):
	task: str
	model: str = 'gpt-4o'
	sensitive: Optional[Dict[str, Any]] = None
	initial_actions: Optional[List[Dict[str, Dict[str, Any]]]] = None
	browser_context_config: Optional[Dict[str, Any]] = None
	return_screenshots: bool = False
	callback_url: Optional[HttpUrl] = None  # validated HTTP/HTTPS URL :contentReference[oaicite:8]{index=8}


class AgentResponse(BaseSettings):
	urls: List[str]
	action_names: List[str]
	errors: List[Optional[str]]
	screenshots: Optional[List[str]] = None
	final_result: Optional[str] = None
	model_actions: Optional[List[Dict[str, Any]]] = None


# ──────────────────────────────────────────────────────────────────────────────
# 4. BACKGROUND WORKER
# ──────────────────────────────────────────────────────────────────────────────
async def process_and_callback(request: AgentRequest):
	# Rebuild LLM & agent kwargs as in original endpoint
	model_name = request.model.lower()
	if model_name.startswith('gpt'):
		from langchain_openai import ChatOpenAI

		llm = ChatOpenAI(model=request.model, api_key=settings.OPENAI_API_KEY)
	else:
		from langchain_google_genai import ChatGoogleGenerativeAI

		llm = ChatGoogleGenerativeAI(model=request.model, api_key=settings.GEMINI_API_KEY)

	agent_kwargs: Dict[str, Any] = {
		'task': request.task,
		'llm': llm,
		'sensitive_data': request.sensitive,
		'initial_actions': request.initial_actions,
	}

	browser = app.state.browser
	if request.browser_context_config:
		cfg = BrowserContextConfig(**request.browser_context_config)
		agent_kwargs['browser_context'] = BrowserContext(browser=browser, config=cfg)
	else:
		agent_kwargs['browser'] = browser

	# Execute the agent
	try:
		agent = Agent(**agent_kwargs)
		history = await agent.run()
		payload = {
			# "urls":          history.urls(),
			# "action_names":  history.action_names(),
			# "errors":        history.errors(),
			# "model_actions": history.model_actions(),
			'final_result': history.final_result(),
		}
		if request.return_screenshots:
			payload['screenshots'] = history.screenshots()
	except Exception as e:
		logger.exception('Agent execution failed')
		payload = {'error': str(e)}

	# POST results to callback_url asynchronously :contentReference[oaicite:9]{index=9}
	async with httpx.AsyncClient() as client:
		try:
			resp = await client.post(str(request.callback_url), json=payload, timeout=200)
			resp.raise_for_status()
		except Exception as exc:
			logger.error(f'Callback to {request.callback_url} failed: {exc}')


# ──────────────────────────────────────────────────────────────────────────────
# 5. RUN AGENT ENDPOINT (now async)
# ──────────────────────────────────────────────────────────────────────────────
@app.post('/run', response_model=Dict[str, Any], status_code=202)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
	# Ensure callback_url provided for async processing :contentReference[oaicite:10]{index=10}
	if not request.callback_url:
		raise HTTPException(status_code=400, detail='callback_url is required for async runs')
	# (Optional) Whitelist domains to prevent SSRF :contentReference[oaicite:11]{index=11}
	# allowed = {"my-service.example.com"}
	# host = httpx.URL(request.callback_url).host
	# if host not in allowed:
	#     raise HTTPException(status_code=400, detail="callback_url domain not allowed")

	background_tasks.add_task(process_and_callback, request)
	return {'status': 'accepted', 'detail': 'Work scheduled'}


# ──────────────────────────────────────────────────────────────────────────────
# 6. ENTRYPOINT FOR UVICORN
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
	import uvicorn

	uvicorn.run('app:app', host=settings.HOST, port=settings.PORT, log_level='info')
