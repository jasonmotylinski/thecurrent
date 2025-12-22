from flask import Flask, send_from_directory, render_template
import dashboard.data as data
import config
from dashboard.routes import api_routes
from dashboard.logging_config import init_logging

app = Flask(__name__, template_folder='templates')
app.register_blueprint(api_routes)

# Initialize logging
init_logging(app)

@app.route('/')
def index():
    app.logger.info('Serving index page')
    return render_template('index.html', station_title='Radio Dashboard')

@app.route('/assets/<path:filename>')
def serve_asset(filename):
    return send_from_directory('assets', filename)



if __name__ == '__main__':
    app.run(debug=config.DEBUG) 