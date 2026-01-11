from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationPreference
import json

class NotificationService:
    @staticmethod
    def create_notification(user, title, message, notification_type='system', 
                           related_object=None, data=None):
        """Create a new notification for a user."""
        
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data or {}
        )
        
        if related_object:
            notification.related_object_type = related_object.__class__.__name__
            notification.related_object_id = str(related_object.id)
            notification.save()
        
        # Send real-time notification
        NotificationService.send_real_time_notification(notification)
        
        # Send platform-specific notifications based on preferences
        NotificationService.send_platform_notifications(notification)
        
        return notification
    
    @staticmethod
    def send_real_time_notification(notification):
        """Send notification via WebSocket."""
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'notifications_{notification.user.uuid}',
            {
                'type': 'send_notification',
                'notification': {
                    'id': str(notification.uuid),
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'created_at': notification.created_at.isoformat(),
                    'data': notification.data
                }
            }
        )
        
        notification.mark_as_sent(platform='web')
    
    @staticmethod
    def send_platform_notifications(notification):
        """Send notifications to other platforms based on user preferences."""
        try:
            preferences = notification.user.notification_preferences
        except NotificationPreference.DoesNotExist:
            preferences = NotificationPreference.objects.create(user=notification.user)
        
        # Check quiet hours
        if preferences.quiet_hours_enabled:
            now = timezone.now().time()
            if preferences.quiet_hours_start <= preferences.quiet_hours_end:
                if preferences.quiet_hours_start <= now <= preferences.quiet_hours_end:
                    return  # Within quiet hours
            else:
                if now >= preferences.quiet_hours_start or now <= preferences.quiet_hours_end:
                    return  # Within quiet hours
        
        # Check notification type preferences
        notification_type = notification.notification_type
        
        if notification_type == 'booking':
            if preferences.email_booking_updates:
                NotificationService.send_email_notification(notification)
            if preferences.push_booking_updates:
                NotificationService.send_push_notification(notification)
            if preferences.desktop_booking_updates:
                NotificationService.send_desktop_notification(notification)
        
        elif notification_type == 'message':
            if preferences.email_messages:
                NotificationService.send_email_notification(notification)
            if preferences.push_messages:
                NotificationService.send_push_notification(notification)
            if preferences.desktop_messages:
                NotificationService.send_desktop_notification(notification)
        
        elif notification_type == 'review':
            if preferences.email_reviews:
                NotificationService.send_email_notification(notification)
            if preferences.push_reviews:
                NotificationService.send_push_notification(notification)
            if preferences.desktop_reviews:
                NotificationService.send_desktop_notification(notification)
        
        elif notification_type == 'promotion':
            if preferences.email_promotions:
                NotificationService.send_email_notification(notification)
            if preferences.push_promotions:
                NotificationService.send_push_notification(notification)
        
        elif notification_type == 'system':
            if preferences.email_system:
                NotificationService.send_email_notification(notification)
    
    @staticmethod
    def send_email_notification(notification):
        """Send notification via email."""
        # TODO: Implement email sending
        # For now, just mark as sent
        notification.mark_as_sent(platform='email')
    
    @staticmethod
    def send_push_notification(notification):
        """Send push notification to mobile devices."""
        # TODO: Implement push notification service (Firebase, APNS)
        notification.mark_as_sent(platform='push')
    
    @staticmethod
    def send_desktop_notification(notification):
        """Send notification to desktop app."""
        # TODO: Implement desktop notification service
        notification.mark_as_sent(platform='desktop')
    
    @staticmethod
    def mark_as_read(notification_ids, user):
        """Mark notifications as read."""
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            user=user
        )
        
        with transaction.atomic():
            for notification in notifications:
                notification.mark_as_read()
    
    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications for a user."""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count()
    
    @staticmethod
    def send_booking_notification(booking, notification_type):
        """Send notification for booking events."""
        if notification_type == 'created':
            title = 'New Booking Request'
            message = f'You have a new booking request for {booking.listing.title}'
        elif notification_type == 'confirmed':
            title = 'Booking Confirmed'
            message = f'Your booking for {booking.listing.title} has been confirmed'
        elif notification_type == 'cancelled':
            title = 'Booking Cancelled'
            message = f'Booking for {booking.listing.title} has been cancelled'
        elif notification_type == 'reminder':
            title = 'Booking Reminder'
            message = f'Your booking for {booking.listing.title} starts tomorrow'
        else:
            return
        
        # Send to guest
        NotificationService.create_notification(
            user=booking.guest,
            title=title,
            message=message,
            notification_type='booking',
            related_object=booking,
            data={'booking_id': str(booking.id)}
        )
        
        # Send to host
        NotificationService.create_notification(
            user=booking.listing.host,
            title=title,
            message=message,
            notification_type='booking',
            related_object=booking,
            data={'booking_id': str(booking.id)}
        )
    
    @staticmethod
    def send_message_notification(message):
        """Send notification for new messages."""
        conversation = message.conversation
        recipients = conversation.participants.exclude(id=message.sender.id)
        
        for recipient in recipients:
            NotificationService.create_notification(
                user=recipient,
                title='New Message',
                message=f'You have a new message from {message.sender.first_name}',
                notification_type='message',
                related_object=message,
                data={
                    'conversation_id': str(conversation.id),
                    'message_id': str(message.id)
                }
            )
    
    @staticmethod
    def send_review_notification(review):
        """Send notification for new reviews."""
        NotificationService.create_notification(
            user=review.reviewee,
            title='New Review',
            message=f'You have a new review from {review.reviewer.first_name}',
            notification_type='review',
            related_object=review,
            data={'review_id': str(review.id)}
        )
