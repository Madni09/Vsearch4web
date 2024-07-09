from flask import Flask, render_template, request, session
from markupsafe import escape
from vsearch import search4letters
import mysql.connector
from ua_parser import user_agent_parser
from DBcm import UseDatabase
from checker import  check_logged_in

from time import sleep

app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                'user': 'vsearch',
                'password': 'vsearchpasswd',
                'database': 'vsearchlogDB',}

def log_request(req: 'flask_request', res: str) -> None:
    
    web_detial = str(request.user_agent)    #Note the code here
    user_browser = user_agent_parser.ParseUserAgent(web_detial)    #Note the code here
    browser = user_browser['family']  


    conn = mysql.connector.connect(**app.config['dbconfig'])
    cursor = conn.cursor()
    
    with UseDatabase(app.config['dbconfig']) as cursor:
        #raise Exception("something awful just happened!!")
        _SQL = """INSERT INTO log
            (phrase, letters, ip, browser_string, results)
            VALUES (%s, %s, %s, %s, %s)"""
        
        

        cursor.execute(_SQL, (req.form['phrase'],
                            req.form['letters'],
                            req.remote_addr,
                            browser,
                            res,    ) )
        conn.commit()
        cursor.close()
        conn.close()



@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results:'
    results = str(search4letters(phrase, letters))
    try:
        log_request(request, results)
    except Exception as err:
        print("***Logging failed due to this error: ", str(err))
    return render_template('results.html',
                           the_phrase = phrase,
                           the_letters = letters,
                           the_title= title,
                           the_results = results, )


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
    the_title='Welcome to search4letters on the web!')

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL ="""select phrase, letters, ip, browser_string, results from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles = ('phrase','letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                                the_title='View Log',
                                the_row_titles=titles,
                                the_data=contents,)
    except Exception as err:
        print('Something went wrong:', str(err))
        
def check_login_status() -> bool:
    if 'logged_in' in session:
        return True
    return False

@app.route('/login')
def do_login() -> set:
   session['logged_in'] = True
   return "You are now logged in!"

@app.route('/logout')
def do_logout() -> set:
    session.pop('logged_in')
    return "You are now logged out!"
app.secret_key = 'YouKnowNothingJohnSnow'

if __name__ == '__main__':
    app.run(debug=True)

