import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def create_intent(amount: float, ride_id: int) -> str:
        if settings.STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
            return f"pi_mock_{ride_id}_secret"
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency="usd",
            metadata={"ride_id": str(ride_id)}
        )
        return intent.id

payment_service = PaymentService()
