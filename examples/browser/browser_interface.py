import asyncio
import sys

from langchain_openai import ChatOpenAI
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig


class CariAIGUI(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
		self.browser = Browser(
			config=BrowserConfig(
				browser_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
			)
		)
		self.agent = None

	def initUI(self):
		self.setWindowTitle('CariAI - Browser Automation')
		self.setGeometry(100, 100, 800, 500)
		layout = QVBoxLayout()

		self.status_label = QLabel("Click 'Start Automation' to begin.")
		layout.addWidget(self.status_label)

		self.log_output = QTextEdit()
		self.log_output.setReadOnly(True)
		self.log_output.setFont(QFont('Arial', 12))
		layout.addWidget(self.log_output)

		self.task_input = QTextEdit()
		self.task_input.setPlaceholderText('Enter automation task...')
		self.task_input.setMinimumHeight(300)
		self.task_input.setFont(QFont('Arial', 12))
		layout.addWidget(self.task_input)

		self.model_input = QLineEdit()
		self.model_input.setPlaceholderText('Enter model name (e.g., gpt-4o)')
		self.model_input.setFont(QFont('Arial', 12))
		layout.addWidget(self.model_input)

		self.start_button = QPushButton('Start Browser Automation')
		self.start_button.clicked.connect(self.run_automation)
		layout.addWidget(self.start_button)

		self.setLayout(layout)

	async def automation_task(self, task, model):
		self.agent = Agent(
			task=task,
			llm=ChatOpenAI(model=model),
			browser=self.browser,
			save_conversation_path='logs/convs',
		)

		self.log_output.append('Starting automation task...')
		history = await self.agent.run()
		await self.browser.close()

		self.log_output.append(f'URL History: {history.urls()}')
		self.log_output.append(f'Total Duration: {history.total_duration_seconds()} seconds')
		self.log_output.append(f'Total Input Tokens: {history.total_input_tokens()}')
		self.log_output.append(f'Model Thoughts: {history.model_actions}')
		self.status_label.setText('Automation Completed.')

	def run_automation(self):
		task = self.task_input.toPlainText()
		model = self.model_input.text()
		if not task or not model:
			self.log_output.append('Error: Please enter both task and model name.')
			return

		self.status_label.setText('Running Automation...')
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(self.automation_task(task, model))
		loop.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = CariAIGUI()
	ex.show()
	sys.exit(app.exec())
