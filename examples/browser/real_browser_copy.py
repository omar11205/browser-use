import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio  # noqa: I001

from langchain_openai import ChatOpenAI

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig

browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		browser_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
	)
)

# new_attributes = [
# 	'title',
# 	'type',
# 	'name',
# 	'role',
# 	'aria-label',
# 	'placeholder',
# 	'value',
# 	'alt',
# 	'aria-expanded',
# 	'data-date-format',
# 	'table',
# 	'button',
# 	'tab',
# 	'tabname',
# 	'issystab',
# ]


async def main():
	agent = Agent(
		task="""In a new Chrome tab go to https://www.epa.gov/chemical-research/pfas-chemical-lists-and-tiered-testing-methods-descriptions and extract from the section "Tiered Testing Methods" 2 methods related to new approach testing methods from PFAS. Then go to docs.google.com create a new document and inside the new document, paste the table information in the way that you consider the best""",  # noqa: E501
		# task="""
		# In a new Chrome tab go to https://www.epa.gov/chemical-research/pfas-chemical-lists-and-tiered-testing-methods-descriptions and extract from the section "Tiered Testing Methods" the entire table related to new approach testing methods from PFAS. Do not miss any table element. Then go to docs.google.com create a new document and inside the new document write the table information.  # noqa: E501
		# """,  # noqa: E501
		# task=""" En Chrome ve a https://www.zoho.com/es-xl/people/ luego accede a ZOHO PEOPLE. En la barra de acciones da click en la opción "Permiso". Encuentra la opción "Vacations" y da click en "Solicitar Permiso", se abrirá una página con un formulario interactivo con menus desplegables y campos de relleno de texto. Usa la siguiente información para llenar el formulario que contiene el nombre del campo a rellenar como llave y como primer elemento del dicionario el tipo de acción para rellenar, si es un campo de relleno de texto ("input_text") o un menu desplegable ("select_dropdown_option"), el segundo elemento del diccionario es el contenido del campo {"Tipo de ausencia": ["select_dropdown_option", "Early Vacation"], "Fecha Inicio": ["input_text", 26-Mar-2025], "Fecha Fin": ["input_text", 27-Mar-2025], "Team Email or Substitute Email": ["input_text", "omarferbol@gmai.com"], "Additional Remarks": ["input_text", "No interrumpir"]}, cuando hayas rellenado el formulatio dale click al botón Cancelar, no le des click en el botón enviar por ningún motivo.  # noqa: E501
		# """,  # noqa: E501
		llm=ChatOpenAI(model='gpt-4o'),
		browser=browser,
		save_conversation_path='logs\\convs',
		# include_attributes=new_attributes,
		use_vision=True,
	)

	history = await agent.run()
	await browser.close()

	# print('url history:--', history.urls())
	# print('total duration:--', history.total_duration_seconds())
	# print('total input tokens:--', history.total_input_tokens())
	# print('input tokens usage:--', history.input_token_usage())
	# print('model outputs:--', history.model_outputs())
	# print('model thoughts:--', history.model_thoughts())
	print('Url screenshots: -- dtype', len(history.screenshots()))

	input('Press Enter to close...')


if __name__ == '__main__':
	asyncio.run(main())
