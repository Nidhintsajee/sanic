from datetime import datetime
from sanic import Sanic, response
from jinja2 import Environment, PackageLoader
from sanic_auth import Auth, User
import pymysql.cursors

app = Sanic(__name__)
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app) 

env = Environment(loader=PackageLoader(__name__, 'templates'))

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='Sanic_demo',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
  
session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session

@app.route('/login', methods=['GET', 'POST'])
async def login(request):
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * from login WHERE username  = '{}' and password = '{}'".format(username,password)
                cur=cursor.execute(sql)
        except Exception as e:
            print(e)
        if cur:
            user = User(id=1, name=username)
            auth.login_user(request, user)
            return response.redirect('/')
        message = 'invalid username or password'
    template = env.get_template('login.html')
    html_content = template.render(message=message)
    return response.html(html_content)

@app.route('/signup', methods=['GET', 'POST'])
async def signup(request):
    message = ''
    if request.method == 'POST':
        fname = request.form.get('fname')
        phoneno = request.form.get('phoneno')
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO login (name,phoneno,username,password) VALUES (%s, %s,%s, %s)"
                cursor.execute(sql, (fname,phoneno,username,password))
                connection.commit()
        except Exception as e:
            print(e)
        return response.redirect('/login')
    template = env.get_template('signup.html')
    html_content = template.render(message=message)
    return response.html(html_content)

@app.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return response.redirect('/login')

@app.route('/')
@auth.login_required(user_keyword='user')
async def profile(request, user):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * from login"
            cursor.execute(sql)
            data = cursor.fetchall()
    except Exception as e:
        print(e)
    template = env.get_template('home.html')
    html_content = template.render(user=user,data=data)
    return response.html(html_content)

def handle_no_auth(request):
    return response.json(dict(message='unauthorized'), status=401)

@app.route('/api/user')
@auth.login_required(user_keyword='user', handle_no_auth=handle_no_auth)
async def api_profile(request, user):
    return response.json(dict(id=user.id, name=user.name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
