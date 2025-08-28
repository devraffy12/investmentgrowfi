"""
Enhanced Authentication Backend with Phone Number Format Policy
Enforces +63XXXXXXXXXX format for all authentication
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from phone_format_policy import PhoneNumberFormatter
import logging

logger = logging.getLogger(__name__)

class PhonePolicyAuthBackend(BaseBackend):
    """
    Custom authentication backend that enforces phone number format policy
    - Normalizes all phone input to +63XXXXXXXXXX
    - Stores all users with +63 format only
    - Supports login with any phone format variation
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with phone number format normalization
        """
        if not username or not password:
            return None
        
        # Normalize the phone number input
        formatter = PhoneNumberFormatter()
        normalized_phone = formatter.normalize_phone_number(username)
        
        if not normalized_phone or not formatter.is_valid_philippine_number(normalized_phone):
            logger.warning(f"Invalid phone number format: {username}")
            return None
        
        try:
            # Always lookup by normalized +63 format
            user = User.objects.get(username=normalized_phone)
            
            # Check password
            if user.check_password(password):
                logger.info(f"Successful authentication for {normalized_phone}")
                return user
            else:
                logger.warning(f"Invalid password for {normalized_phone}")
                return None
                
        except User.DoesNotExist:
            logger.warning(f"User not found: {normalized_phone}")
            return None
        except Exception as e:
            logger.error(f"Authentication error for {normalized_phone}: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID for session management
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class PhonePolicyUserManager:
    """
    User management utilities that enforce phone format policy
    """
    
    @staticmethod
    def create_user_with_phone_policy(phone_input, password, email=None, **extra_fields):
        """
        Create user with enforced phone number format policy
        """
        formatter = PhoneNumberFormatter()
        normalized_phone = formatter.normalize_phone_number(phone_input)
        
        if not normalized_phone or not formatter.is_valid_philippine_number(normalized_phone):
            raise ValueError(f"Invalid phone number format: {phone_input}")
        
        # Check if user already exists
        if User.objects.filter(username=normalized_phone).exists():
            raise ValueError(f"User already exists: {normalized_phone}")
        
        # Create user with normalized phone as username
        user = User.objects.create_user(
            username=normalized_phone,
            email=email or f"{normalized_phone[3:]}@growfi.com",  # Remove +63 for email
            password=password,
            **extra_fields
        )
        
        logger.info(f"Created user with normalized phone: {normalized_phone}")
        return user
    
    @staticmethod
    def update_user_phone_format(user):
        """
        Update existing user to use proper phone format
        """
        formatter = PhoneNumberFormatter()
        current_username = user.username
        
        # Skip if already in correct format
        if formatter.is_valid_philippine_number(current_username):
            return user
        
        # Normalize the current username
        normalized_phone = formatter.normalize_phone_number(current_username)
        
        if not normalized_phone:
            logger.error(f"Cannot normalize phone for user: {current_username}")
            return user
        
        # Check if normalized version already exists
        if User.objects.filter(username=normalized_phone).exclude(pk=user.pk).exists():
            logger.error(f"Normalized phone already exists: {normalized_phone}")
            return user
        
        # Update username to normalized format
        user.username = normalized_phone
        user.save()
        
        logger.info(f"Updated user phone format: {current_username} -> {normalized_phone}")
        return user
