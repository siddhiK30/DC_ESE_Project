from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/rpc", methods=["POST"])
def rpc():
    data = request.get_json()
    return jsonify({
        "timestamp": "2025-05-03T19:00:00",
        "message": "Synchronized timestamp from rpc-server-3"
    })

if __name__ == "__main__":
    app.run(port=8003)
