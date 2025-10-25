from fastapi import APIRouter, BackgroundTasks
from app.services.email_service import email_service
from app.repositories.user_profile_repository import UserProfileRepository, AddressRepository
from app.core.database import get_database
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-address-reminders")
async def send_address_reminders(background_tasks: BackgroundTasks):
    """Send 24-hour address completion reminders to users without default addresses"""
    
    try:
        db = get_database()
        user_repo = UserProfileRepository(db)
        address_repo = AddressRepository(db)
        
        # Find users created 24 hours ago without default addresses
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Get users from the last 24-48 hours (to avoid spamming)
        start_time = cutoff_time - timedelta(hours=24)
        
        # Query users created in the time window
        users_cursor = user_repo.users.find({
            "created_at": {
                "$gte": start_time.isoformat(),
                "$lte": cutoff_time.isoformat()
            },
            "is_active": True,
            "$or": [
                {"defaultAddressId": {"$exists": False}},
                {"defaultAddressId": None}
            ]
        })
        
        users_data = await users_cursor.to_list(length=100)  # Limit to prevent spam
        reminder_count = 0
        
        for user_data in users_data:
            # Double-check they don't have addresses
            address_count = await address_repo.count_user_addresses(user_data["id"])
            
            if address_count == 0:
                # Send reminder email
                display_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                
                background_tasks.add_task(
                    email_service.send_address_reminder_email,
                    email=user_data["email"],
                    display_name=display_name
                )
                
                reminder_count += 1
                logger.info(f"Address reminder queued for {user_data['email']}")
        
        return {
            "status": "success",
            "reminders_sent": reminder_count,
            "message": f"Address reminders queued for {reminder_count} users"
        }
        
    except Exception as e:
        logger.error(f"Error sending address reminders: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to send reminders"
        }