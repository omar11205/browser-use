import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.post('/callback')
async def receive_callback(request: Request):
	payload = await request.json()
	# do whatever you need with the payload
	print('=== CALLBACK RECEIVED ===')
	print(payload)
	return {'status': 'received'}


if __name__ == '__main__':
	uvicorn.run('callback_server:app', host='0.0.0.0', port=8888, reload=True)
