import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { CheckCircle as CheckCircleIcon, Schedule as ClockIcon, Warning as ExclamationCircleIcon } from '@mui/icons-material';

interface UPIPaymentProps {
  amount: number;
  description: string;
  onSuccess: (paymentId: string) => void;
  onError: (error: string) => void;
  userEmail?: string;
  userPhone?: string;
  userName?: string;
  referenceId?: string;
}

interface PaymentRequest {
  payment_id: string;
  amount: number;
  upi_id: string;
  upi_name: string;
  payment_note: string;
  qr_code_base64: string;
  upi_deep_link: string;
  expires_at: string;
  instructions: string[];
  require_screenshot: boolean;
}

const UPIPayment: React.FC<UPIPaymentProps> = ({
  amount,
  description,
  onSuccess,
  onError,
  userEmail,
  userPhone,
  userName,
  referenceId
}) => {
  const [paymentRequest, setPaymentRequest] = useState<PaymentRequest | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState<'create' | 'payment' | 'proof' | 'verification'>('create');
  const [transactionId, setTransactionId] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [paymentStatus, setPaymentStatus] = useState<string>('');

  useEffect(() => {
    createPaymentRequest();
  }, []);

  useEffect(() => {
    if (paymentRequest && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft, paymentRequest]);

  const createPaymentRequest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/payments/upi/create-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount,
          description,
          email: userEmail,
          phone: userPhone,
          name: userName,
          reference_id: referenceId,
          ip_address: await getClientIP(),
          user_agent: navigator.userAgent
        }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setPaymentRequest(data.data);
        setStep('payment');
        
        // Calculate time left
        const expiresAt = new Date(data.data.expires_at);
        const now = new Date();
        const timeLeftSeconds = Math.max(0, Math.floor((expiresAt.getTime() - now.getTime()) / 1000));
        setTimeLeft(timeLeftSeconds);
      } else {
        onError(data.message || 'Failed to create payment request');
      }
    } catch (error) {
      onError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  };

  const submitPaymentProof = async () => {
    if (!transactionId.trim()) {
      alert('Please enter the transaction ID');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('transaction_id', transactionId);
      if (paymentMethod) formData.append('payment_method', paymentMethod);
      if (screenshot) formData.append('screenshot', screenshot);

      const response = await fetch(`/api/v1/payments/upi/submit-proof/${paymentRequest?.payment_id}`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setStep('verification');
        setPaymentStatus(data.data.payment_status);
        
        if (data.data.auto_verified) {
          onSuccess(paymentRequest!.payment_id);
        } else {
          // Start polling for verification status
          pollPaymentStatus();
        }
      } else {
        onError(data.message || 'Failed to submit payment proof');
      }
    } catch (error) {
      onError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async () => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/payments/upi/status/${paymentRequest?.payment_id}`);
        const data = await response.json();
        
        if (data.status === 'success') {
          const status = data.data.status;
          setPaymentStatus(status);
          
          if (status === 'success') {
            clearInterval(pollInterval);
            onSuccess(paymentRequest!.payment_id);
          } else if (status === 'failed') {
            clearInterval(pollInterval);
            onError('Payment verification failed');
          }
        }
      } catch (error) {
        console.error('Error polling payment status:', error);
      }
    }, 5000); // Poll every 5 seconds

    // Stop polling after 10 minutes
    setTimeout(() => clearInterval(pollInterval), 600000);
  };

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const openUPIApp = () => {
    if (paymentRequest?.upi_deep_link) {
      window.open(paymentRequest.upi_deep_link, '_blank');
    }
  };

  if (loading && !paymentRequest) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Creating payment request...</span>
      </div>
    );
  }

  if (step === 'create') {
    return (
      <div className="text-center p-8">
        <button
          onClick={createPaymentRequest}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          Create Payment Request
        </button>
      </div>
    );
  }

  if (step === 'payment' && paymentRequest) {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">UPI Payment</h3>
          <p className="text-2xl font-bold text-green-600">₹{paymentRequest.amount}</p>
          <p className="text-sm text-gray-600">{paymentRequest.payment_note}</p>
        </div>

        {timeLeft > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <div className="flex items-center">
              <ClockIcon className="h-5 w-5 text-yellow-600 mr-2" />
              <span className="text-sm text-yellow-800">
                Time remaining: {formatTime(timeLeft)}
              </span>
            </div>
          </div>
        )}

        <div className="text-center mb-6">
          <div className="inline-block p-4 bg-white border-2 border-gray-200 rounded-lg">
            <img
              src={`data:image/png;base64,${paymentRequest.qr_code_base64}`}
              alt="UPI QR Code"
              className="w-48 h-48"
            />
          </div>
        </div>

        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Pay to:</span>
            <span className="font-medium">{paymentRequest.upi_name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">UPI ID:</span>
            <span className="font-medium">{paymentRequest.upi_id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Amount:</span>
            <span className="font-medium">₹{paymentRequest.amount}</span>
          </div>
        </div>

        <button
          onClick={openUPIApp}
          className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 mb-4"
        >
          Pay with UPI App
        </button>

        <div className="border-t pt-4">
          <h4 className="font-medium text-gray-900 mb-2">Instructions:</h4>
          <ol className="text-sm text-gray-600 space-y-1">
            {paymentRequest.instructions.map((instruction, index) => (
              <li key={index}>{instruction}</li>
            ))}
          </ol>
        </div>

        <button
          onClick={() => setStep('proof')}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 mt-4"
        >
          I have completed the payment
        </button>
      </div>
    );
  }

  if (step === 'proof' && paymentRequest) {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Submit Payment Proof</h3>
          <p className="text-sm text-gray-600">Payment ID: {paymentRequest.payment_id}</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Transaction ID *
            </label>
            <input
              type="text"
              value={transactionId}
              onChange={(e) => setTransactionId(e.target.value)}
              placeholder="Enter UPI transaction ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payment Method
            </label>
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select UPI app used</option>
              <option value="phonepe">PhonePe</option>
              <option value="googlepay">Google Pay</option>
              <option value="paytm">Paytm</option>
              <option value="bhim">BHIM</option>
              <option value="amazon_pay">Amazon Pay</option>
              <option value="other">Other</option>
            </select>
          </div>

          {paymentRequest.require_screenshot && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Screenshot
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setScreenshot(e.target.files?.[0] || null)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Upload screenshot of successful payment
              </p>
            </div>
          )}
        </div>

        <button
          onClick={submitPaymentProof}
          disabled={loading || !transactionId.trim()}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed mt-6"
        >
          {loading ? 'Submitting...' : 'Submit Payment Proof'}
        </button>
      </div>
    );
  }

  if (step === 'verification') {
    return (
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 text-center">
        {paymentStatus === 'success' ? (
          <>
            <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Successful!</h3>
            <p className="text-sm text-gray-600">
              Your payment has been verified and processed successfully.
            </p>
          </>
        ) : paymentStatus === 'failed' ? (
          <>
            <ExclamationCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Failed</h3>
            <p className="text-sm text-gray-600">
              Your payment could not be verified. Please contact support.
            </p>
          </>
        ) : (
          <>
            <ClockIcon className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Verification Pending</h3>
            <p className="text-sm text-gray-600">
              Your payment is being verified. This may take a few minutes.
            </p>
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mt-4"></div>
          </>
        )}
      </div>
    );
  }

  return null;
};

export default UPIPayment;
