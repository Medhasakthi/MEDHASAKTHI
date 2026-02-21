/**
 * Payment Gateway Component for Talent Exam Registrations
 * Handles payment processing for student registrations
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Divider,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio
} from '@mui/material';
import {
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  CreditCard as CreditCardIcon,
  AccountBalance as BankIcon,
  Wallet as WalletIcon,
  QrCode as QrCodeIcon
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

// Types
interface PaymentDetails {
  registrationIds: string[];
  examTitle: string;
  examCode: string;
  studentCount: number;
  registrationFee: number;
  totalAmount: number;
  taxes: number;
  finalAmount: number;
  instituteName: string;
  instituteCode: string;
}

interface PaymentMethod {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  processingFee: number;
  isAvailable: boolean;
}

interface PaymentResponse {
  success: boolean;
  transactionId: string;
  paymentId: string;
  status: string;
  message: string;
  receiptUrl?: string;
}

const PAYMENT_METHODS: PaymentMethod[] = [
  {
    id: 'razorpay',
    name: 'Credit/Debit Card',
    icon: <CreditCardIcon />,
    description: 'Pay using Credit Card, Debit Card, or Net Banking',
    processingFee: 2.5,
    isAvailable: true
  },
  {
    id: 'upi',
    name: 'UPI Payment',
    icon: <QrCodeIcon />,
    description: 'Pay using UPI apps like GPay, PhonePe, Paytm',
    processingFee: 0,
    isAvailable: true
  },
  {
    id: 'netbanking',
    name: 'Net Banking',
    icon: <BankIcon />,
    description: 'Pay directly from your bank account',
    processingFee: 1.5,
    isAvailable: true
  },
  {
    id: 'wallet',
    name: 'Digital Wallet',
    icon: <WalletIcon />,
    description: 'Pay using Paytm, Amazon Pay, or other wallets',
    processingFee: 1.0,
    isAvailable: true
  }
];

interface PaymentGatewayProps {
  paymentDetails: PaymentDetails;
  onPaymentSuccess: (response: PaymentResponse) => void;
  onPaymentFailure: (error: string) => void;
}

export const PaymentGateway: React.FC<PaymentGatewayProps> = ({
  paymentDetails,
  onPaymentSuccess,
  onPaymentFailure
}) => {
  const [selectedMethod, setSelectedMethod] = useState<string>('razorpay');
  const [processing, setProcessing] = useState(false);
  const [paymentStep, setPaymentStep] = useState<'select' | 'process' | 'success' | 'failed'>('select');
  const [transactionDetails, setTransactionDetails] = useState<PaymentResponse | null>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);

  const calculateProcessingFee = (methodId: string, amount: number) => {
    const method = PAYMENT_METHODS.find(m => m.id === methodId);
    if (!method) return 0;
    return (amount * method.processingFee) / 100;
  };

  const calculateFinalAmount = () => {
    const processingFee = calculateProcessingFee(selectedMethod, paymentDetails.totalAmount);
    return paymentDetails.totalAmount + processingFee;
  };

  const initializePayment = async () => {
    setProcessing(true);
    setPaymentStep('process');

    try {
      // Initialize payment with selected method
      const paymentData = {
        amount: calculateFinalAmount(),
        currency: 'INR',
        registrationIds: paymentDetails.registrationIds,
        examCode: paymentDetails.examCode,
        paymentMethod: selectedMethod,
        instituteName: paymentDetails.instituteName,
        instituteCode: paymentDetails.instituteCode
      };

      // API call to create payment order
      // const response = await api.post('/payments/create-order', paymentData);
      
      // Mock payment processing
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Simulate payment success/failure
      const isSuccess = Math.random() > 0.1; // 90% success rate for demo
      
      if (isSuccess) {
        const successResponse: PaymentResponse = {
          success: true,
          transactionId: `TXN${Date.now()}`,
          paymentId: `PAY${Date.now()}`,
          status: 'completed',
          message: 'Payment completed successfully',
          receiptUrl: `/receipts/TXN${Date.now()}.pdf`
        };
        
        setTransactionDetails(successResponse);
        setPaymentStep('success');
        onPaymentSuccess(successResponse);
        toast.success('Payment completed successfully!');
      } else {
        const errorMessage = 'Payment failed. Please try again.';
        setPaymentStep('failed');
        onPaymentFailure(errorMessage);
        toast.error(errorMessage);
      }
    } catch (error) {
      const errorMessage = 'Payment processing failed. Please try again.';
      setPaymentStep('failed');
      onPaymentFailure(errorMessage);
      toast.error(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  const retryPayment = () => {
    setPaymentStep('select');
    setTransactionDetails(null);
  };

  const downloadReceipt = () => {
    if (transactionDetails?.receiptUrl) {
      window.open(transactionDetails.receiptUrl, '_blank');
    }
  };

  const renderPaymentMethodSelection = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Select Payment Method
        </Typography>
        
        <RadioGroup
          value={selectedMethod}
          onChange={(e) => setSelectedMethod(e.target.value)}
        >
          {PAYMENT_METHODS.map((method) => (
            <Card
              key={method.id}
              variant="outlined"
              sx={{
                mb: 2,
                cursor: method.isAvailable ? 'pointer' : 'not-allowed',
                opacity: method.isAvailable ? 1 : 0.5,
                border: selectedMethod === method.id ? 2 : 1,
                borderColor: selectedMethod === method.id ? 'primary.main' : 'divider'
              }}
              onClick={() => method.isAvailable && setSelectedMethod(method.id)}
            >
              <CardContent sx={{ py: 2 }}>
                <FormControlLabel
                  value={method.id}
                  control={<Radio />}
                  disabled={!method.isAvailable}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Box sx={{ mr: 2, color: 'primary.main' }}>
                        {method.icon}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {method.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {method.description}
                        </Typography>
                        {method.processingFee > 0 && (
                          <Typography variant="caption" color="warning.main">
                            Processing fee: {method.processingFee}%
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  }
                />
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </CardContent>
    </Card>
  );

  const renderPaymentSummary = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Payment Summary
        </Typography>
        
        <TableContainer>
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell>Exam</TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {paymentDetails.examTitle}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {paymentDetails.examCode}
                  </Typography>
                </TableCell>
              </TableRow>
              
              <TableRow>
                <TableCell>Number of Students</TableCell>
                <TableCell align="right">{paymentDetails.studentCount}</TableCell>
              </TableRow>
              
              <TableRow>
                <TableCell>Registration Fee (per student)</TableCell>
                <TableCell align="right">₹{paymentDetails.registrationFee}</TableCell>
              </TableRow>
              
              <TableRow>
                <TableCell>Subtotal</TableCell>
                <TableCell align="right">₹{paymentDetails.totalAmount}</TableCell>
              </TableRow>
              
              {paymentDetails.taxes > 0 && (
                <TableRow>
                  <TableCell>Taxes & Fees</TableCell>
                  <TableCell align="right">₹{paymentDetails.taxes}</TableCell>
                </TableRow>
              )}
              
              {calculateProcessingFee(selectedMethod, paymentDetails.totalAmount) > 0 && (
                <TableRow>
                  <TableCell>Processing Fee</TableCell>
                  <TableCell align="right">
                    ₹{calculateProcessingFee(selectedMethod, paymentDetails.totalAmount).toFixed(2)}
                  </TableCell>
                </TableRow>
              )}
              
              <TableRow>
                <TableCell colSpan={2}>
                  <Divider />
                </TableCell>
              </TableRow>
              
              <TableRow>
                <TableCell>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Total Amount
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="subtitle1" fontWeight="bold">
                    ₹{calculateFinalAmount().toFixed(2)}
                  </Typography>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
        
        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            fullWidth
            size="large"
            startIcon={<PaymentIcon />}
            onClick={() => setConfirmDialogOpen(true)}
            disabled={processing}
          >
            Proceed to Pay ₹{calculateFinalAmount().toFixed(2)}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderProcessingState = () => (
    <Card>
      <CardContent sx={{ textAlign: 'center', py: 6 }}>
        <CircularProgress size={60} sx={{ mb: 3 }} />
        <Typography variant="h6" gutterBottom>
          Processing Payment...
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Please wait while we process your payment. Do not close this window.
        </Typography>
      </CardContent>
    </Card>
  );

  const renderSuccessState = () => (
    <Card>
      <CardContent sx={{ textAlign: 'center', py: 6 }}>
        <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
        <Typography variant="h5" gutterBottom color="success.main">
          Payment Successful!
        </Typography>
        <Typography variant="body1" paragraph>
          Your payment has been processed successfully. All {paymentDetails.studentCount} students have been registered for the exam.
        </Typography>
        
        {transactionDetails && (
          <Box sx={{ mt: 3, mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Transaction ID: {transactionDetails.transactionId}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Payment ID: {transactionDetails.paymentId}
            </Typography>
          </Box>
        )}
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<ReceiptIcon />}
            onClick={downloadReceipt}
          >
            Download Receipt
          </Button>
          <Button
            variant="contained"
            onClick={() => window.location.href = '/talent-exams'}
          >
            Back to Exams
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const renderFailedState = () => (
    <Card>
      <CardContent sx={{ textAlign: 'center', py: 6 }}>
        <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
        <Typography variant="h5" gutterBottom color="error.main">
          Payment Failed
        </Typography>
        <Typography variant="body1" paragraph>
          We couldn't process your payment. Please try again with a different payment method.
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            onClick={retryPayment}
          >
            Try Again
          </Button>
          <Button
            variant="contained"
            onClick={() => window.location.href = '/talent-exams'}
          >
            Back to Exams
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Payment Gateway
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Complete the payment to confirm registration for all selected students.
      </Alert>
      
      <Grid container spacing={3}>
        {paymentStep === 'select' && (
          <>
            <Grid item xs={12} md={7}>
              {renderPaymentMethodSelection()}
            </Grid>
            <Grid item xs={12} md={5}>
              {renderPaymentSummary()}
            </Grid>
          </>
        )}
        
        {paymentStep === 'process' && (
          <Grid item xs={12}>
            {renderProcessingState()}
          </Grid>
        )}
        
        {paymentStep === 'success' && (
          <Grid item xs={12}>
            {renderSuccessState()}
          </Grid>
        )}
        
        {paymentStep === 'failed' && (
          <Grid item xs={12}>
            {renderFailedState()}
          </Grid>
        )}
      </Grid>

      {/* Payment Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirm Payment</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            You are about to pay ₹{calculateFinalAmount().toFixed(2)} for registering {paymentDetails.studentCount} students in {paymentDetails.examTitle}.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This payment is non-refundable. Please ensure all student details are correct before proceeding.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              setConfirmDialogOpen(false);
              initializePayment();
            }}
            disabled={processing}
          >
            Confirm & Pay
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
