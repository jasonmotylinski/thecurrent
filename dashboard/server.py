from flask import Flask, send_from_directory, render_template
import atexit
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


def shutdown_engine():
    """Cleanly dispose of the database engine on shutdown.

    This ensures all PostgreSQL connections are properly closed when the
    application terminates, rather than being left in a hanging state.
    """
    engine = data.get_engine()
    if engine:
        engine.dispose()
        app.logger.info('Database engine disposed on shutdown')


# Register cleanup handler
atexit.register(shutdown_engine)


if __name__ == '__main__':
    app.run(debug=config.DEBUG) 