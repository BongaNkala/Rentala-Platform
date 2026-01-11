import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Conversation
import asyncio

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Get conversation ID from URL
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send last 50 messages
        messages = await self.get_messages()
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages
        }))
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': str(self.user.uuid),
                'status': 'online'
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others that user left
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': str(self.user.uuid),
                    'status': 'offline'
                }
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            message = data['message']
            
            # Save message to database
            saved_message = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(saved_message.id),
                        'sender': str(saved_message.sender.uuid),
                        'content': saved_message.content,
                        'timestamp': saved_message.timestamp.isoformat(),
                        'is_read': saved_message.is_read
                    }
                }
            )
        
        elif message_type == 'typing':
            # Broadcast typing status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'user_id': str(self.user.uuid),
                    'is_typing': data['is_typing']
                }
            )
        
        elif message_type == 'read_receipt':
            # Mark messages as read
            message_ids = data.get('message_ids', [])
            await self.mark_as_read(message_ids)
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def user_status(self, event):
        # Send user status update
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'status': event['status']
        }))
    
    async def typing_status(self, event):
        # Send typing status
        await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'user_id': event['user_id'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def get_messages(self):
        messages = Message.objects.filter(
            conversation_id=self.conversation_id
        ).select_related('sender').order_by('timestamp')[:50]
        
        return [
            {
                'id': str(msg.id),
                'sender': str(msg.sender.uuid),
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read
            }
            for msg in messages
        ]
    
    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        return message
    
    @database_sync_to_async
    def mark_as_read(self, message_ids):
        Message.objects.filter(
            id__in=message_ids,
            conversation_id=self.conversation_id
        ).update(is_read=True)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group_name = f'notifications_{self.user.uuid}'
        
        # Join user's notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications
        notifications = await self.get_unread_notifications()
        await self.send(text_data=json.dumps({
            'type': 'notification_history',
            'notifications': notifications
        }))
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_as_read':
            notification_ids = data.get('notification_ids', [])
            await self.mark_notifications_as_read(notification_ids)
    
    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def get_unread_notifications(self):
        from notifications.models import Notification
        notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).order_by('-created_at')[:20]
        
        return [
            {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.isoformat(),
                'data': notification.data
            }
            for notification in notifications
        ]
    
    @database_sync_to_async
    def mark_notifications_as_read(self, notification_ids):
        from notifications.models import Notification
        Notification.objects.filter(
            id__in=notification_ids,
            user=self.user
        ).update(is_read=True)
