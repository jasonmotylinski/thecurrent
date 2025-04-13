from flask import Flask, send_from_directory, jsonify
import dashboard.data as data
import config
from dashboard.routes import api_routes

app = Flask(__name__)
app.register_blueprint(api_routes)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/assets/<path:filename>')
def serve_asset(filename):
    return send_from_directory('assets', filename)

@app.route('/api/last_updated')
def last_updated():
    last_update = data.get_last_updated()
    return jsonify({
        'last_updated': last_update.isoformat()
    })

if __name__ == '__main__':
    app.run(debug=config.DEBUG) 