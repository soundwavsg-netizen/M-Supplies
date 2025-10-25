from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    message: str

class ContactFormResponse(BaseModel):
    status: str
    message: str

@router.post("/contact", response_model=ContactFormResponse)
async def submit_contact_form(
    form_data: ContactFormRequest,
    background_tasks: BackgroundTasks
):
    """Submit contact form and send notification email"""
    
    try:
        # Add email sending to background tasks
        background_tasks.add_task(
            email_service.send_contact_form_notification,
            name=form_data.name,
            email=form_data.email,
            message=form_data.message
        )
        
        logger.info(f"Contact form submitted by {form_data.name} ({form_data.email})")
        
        return ContactFormResponse(
            status="success",
            message="Thanks for reaching out! We'll reply soon."
        )
        
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to submit form. Please try again later."
        )