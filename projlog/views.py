from projlog import app

@app.route('/')
@app.route('/index')
def index():
    return "Get back to work Sameer"