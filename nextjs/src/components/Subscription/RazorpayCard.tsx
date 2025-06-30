import React, { useState } from "react";
export default function RazorpayComponent() {
  const [amount, setAmount] = useState("");

  const handlePayment = async () => {
    // const res = await fetch("/api/createOrder", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ amount, currency: "INR" }),
    // });

    // const order = await res.json();

    // if (!order.id) throw new Error("Unable to create order");

    // const script = document.createElement("script");
    // script.src = "https://checkout.razorpay.com/v1/checkout.js";
    // script.onload = () => {
    //   const options = {
    //     key: config.RAZORPAY.KEY_ID,
    //     amount: order.amount,
    //     currency: order.currency,
    //     name: "Test Payment",
    //     description: "Testing Razorpay Integration",
    //     order_id: order.id,
    //     handler: (response) => {
    //       alert(`Payment successful! Payment ID: ${response.razorpay_payment_id}`);
    //     },
    //     prefill: {
    //       name: "Test User",
    //       email: "test@example.com",
    //       contact: "9999999999",
    //     },
    //     theme: { color: "#3399cc" },
    //   };

    //   const rzp = new window.Razorpay(options);
    //   rzp.open();
    // };
    // document.body.appendChild(script);
  };

  return (
    <div className="flex w-screen h-screen items-center justify-center flex-col gap-4">
      <h1>Razorpay Payment Test</h1>
      <input
        type="number"
        placeholder="Enter amount"
        className="px-4 py-2 rounded-md text-black"
        value={amount}
        onChange={(e) => setAmount(Number(e.target.value))}
      />
      <button
        className="bg-green-500 text-white px-4 py-2 rounded-md"
        onClick={handlePayment}
      >
        Create Order
      </button>
    </div>
  );
}
