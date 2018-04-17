from jinja2 import Environment, PackageLoader
from sanic import Sanic
from sanic.response import html

env = Environment(loader=PackageLoader('hello', 'templates'))

app = Sanic(__name__)

@app.route('/')
async def hello(request):
	template = env.get_template('message.html')
	html_content = template.render(message="Hello world!")
	return html(html_content)

@app.route('/welcome')
async def welcome(request):
	template = env.get_template('welcome.html')
	html_content = template.render(message="welcome")
	return html(html_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010, debug=True, workers=1)
