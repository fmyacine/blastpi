from flask import Flask, jsonify, send_from_directory, request,send_file
from flask_cors import CORS
import simplejson as json
import requests
import dotenv
import os

# Load .env variables
dotenv.load_dotenv()
apikey = os.getenv("apikey")

header = {
    'Authorization': f"Key {apikey}"
}

app = Flask(__name__, static_folder="./build", static_url_path="/")
CORS(app)

@app.route("/validation-key.txt")
def serve_validation_file():
    return Response(
        "ebcfc01f76ba11ce6fb8ee0964c98b7b14f3a47f49c0e8255bb2e44f15f260e6bd64fd3fb2ffbb82e6c8be8ffc647a4a5d4f86263188193d5c03f66f80314bcb",
        mimetype="text/plain"
    )
    
# Example API endpoint
@app.route("/api/hello")
def hello():
    return jsonify(message="Hello from Flask API!")

# Serve React app only on root "/"
@app.route("/")
def serve_react():
    print(apikey)
    return send_from_directory(app.static_folder, "index.html")

@app.route('/payment/approve', methods=['POST'])
def approve():
    try:
        # Read JSON data from frontend
        data = request.get_json()
        
        if not data:
            return jsonify(status="error", message="No JSON data provided"), 400
            
        paymentId = data.get("paymentId")
        
        if not paymentId:
            return jsonify(status="error", message="Missing paymentId"), 400

        print(f"Approving payment: {paymentId}")

        # Approve the payment using your server key
        approveurl = f"https://api.minepi.com/v2/payments/{paymentId}/approve"
        response = requests.post(approveurl, headers=header)

        print(f"Pi API approve response: {response.status_code} - {response.text}")

        # Check if Pi API request was successful
        if response.status_code == 200:
            return jsonify(status="ok", message="Payment approved"), 200
        else:
            print(f"Pi API error: {response.text}")
            return jsonify(status="error", message="Pi API approval failed", details=response.text), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Network error during approve: {e}")
        return jsonify(status="error", message="Network error"), 500
    except Exception as e:
        print(f"Approve endpoint error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/payment/complete', methods=['POST'])
def complete():
    try:
        # Read JSON data from frontend
        data = request.get_json()
        
        if not data:
            return jsonify(status="error", message="No JSON data provided"), 400
            
        paymentId = data.get('paymentId')
        txid = data.get('txid')
        
        if not paymentId or not txid:
            return jsonify(status="error", message="Missing paymentId or txid"), 400

        print(f"Completing payment: {paymentId} with txid: {txid}")

        # Complete the payment using your server key
        completeurl = f"https://api.minepi.com/v2/payments/{paymentId}/complete"
        
        # Pi API expects JSON data for complete endpoint
        complete_data = {'txid': txid}
        response = requests.post(completeurl, headers={**header, 'Content-Type': 'application/json'}, json=complete_data)
        
        print(f"Pi API complete response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            # Parse the response to get payment details
            try:
                payment_data = response.json()
                return jsonify(status="ok", message="Payment completed", payment=payment_data), 200
            except json.JSONDecodeError:
                return jsonify(status="ok", message="Payment completed"), 200
        else:
            print(f"Pi API complete error: {response.text}")
            return jsonify(status="error", message="Pi API completion failed", details=response.text), response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Network error during complete: {e}")
        return jsonify(status="error", message="Network error"), 500
    except Exception as e:
        print(f"Complete endpoint error: {e}")
        return jsonify(status="error", message=str(e)), 500


@app.route('/payment/cancel', methods=['POST'])
def cancel():
    try:
        data = request.get_json()
        if not data:
            return jsonify(status="error", message="No JSON data provided"), 400
            
        paymentId = data.get('paymentId')
        if not paymentId:
            return jsonify(status="error", message="Missing paymentId"), 400

        print(f"Cancelling payment: {paymentId}")
        
        cancelurl = f"https://api.minepi.com/v2/payments/{paymentId}/cancel"
        response = requests.post(cancelurl, headers=header)
        
        print(f"Pi API cancel response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            return jsonify(status="ok", message="Payment cancelled"), 200
        else:
            return jsonify(status="error", message="Pi API cancellation failed"), response.status_code
            
    except Exception as e:
        print(f"Cancel endpoint error: {e}")
        return jsonify(status="error", message=str(e)), 500


# Optional: Get user info endpoint
@app.route('/api/user/me', methods=['GET'])
def get_user_info():
    try:
        # Get access token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify(status="error", message="Missing or invalid Authorization header"), 401
            
        access_token = auth_header.replace('Bearer ', '')
        
        userheader = {"Authorization": f"Bearer {access_token}"}
        userurl = "https://api.minepi.com/v2/me"
        
        response = requests.get(userurl, headers=userheader)
        
        if response.status_code == 200:
            user_data = response.json()
            return jsonify(status="ok", user=user_data), 200
        else:
            return jsonify(status="error", message="Failed to fetch user info"), response.status_code
            
    except Exception as e:
        print(f"User info endpoint error: {e}")
        return jsonify(status="error", message=str(e)), 500


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)




