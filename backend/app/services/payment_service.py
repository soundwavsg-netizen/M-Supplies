import stripe
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Dict, Any

stripe.api_key = settings.stripe_secret_key

class PaymentService:
    @staticmethod
    async def create_payment_intent(amount: float, currency: str = "sgd", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a Stripe payment intent"""
        try:
            # Stripe expects amount in cents
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
    
    @staticmethod
    async def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a payment intent status"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,  # Convert back to dollars
                'currency': intent.currency
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
    
    @staticmethod
    async def refund_payment(payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a refund for a payment"""
        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount:
                refund_data['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100
            }
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
