from flask import Flask, request, jsonify
import razorpay
import hmac
import hashlib
import time

app = Flask(__name__)

# Razorpay credentials (Test Mode for development)
RAZORPAY_KEY_ID = "YOUR_KEY_ID"
RAZORPAY_KEY_SECRET = "YOUR_KEY_SECRET"

# Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.json
    amount = data.get("amount")  # in INR

    order_data = {
        "amount": int(amount * 100),  # convert to paise
        "currency": "INR",
        "receipt": f"order_rcptid_{int(time.time())}",
        "payment_capture": 1
    }
    order = razorpay_client.order.create(data=order_data)
    return jsonify(order)


@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    body = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected_signature == signature:
        # Store enrollment in DB here
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"}), 400


if __name__ == "__main__":
    app.run(port=5000, debug=True)
