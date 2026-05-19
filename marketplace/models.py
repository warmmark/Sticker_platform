from django.conf import settings
from django.db import models
from django.db.models import Q


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    nickname = models.CharField(max_length=80, blank=True)
    about = models.TextField(blank=True)
    telegram_url = models.URLField(blank=True)
    vk_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname or self.user.username


class Listing(models.Model):
    class Category(models.TextChoices):
        STICKERS = 'stickers', 'Стикер-пак'
        EMOJI = 'emoji', 'Эмоджи-пак'

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deadline_days = models.PositiveSmallIntegerField(default=7)
    preview_image = models.ImageField(upload_to='listing_previews/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['seller', 'category'],
                condition=Q(is_active=True),
                name='unique_active_listing_per_category_per_seller',
            )
        ]

    def __str__(self):
        return self.title


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'listing'], name='unique_favorite_per_user')]

    def __str__(self):
        return f'{self.user} -> {self.listing}'


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Создан'
        ACCEPTED = 'accepted', 'Принят'
        IN_PROGRESS = 'in_progress', 'В работе'
        WAITING_APPROVAL = 'waiting_approval', 'Ожидает подтверждения'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name='orders')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_orders')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_orders')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id}: {self.listing}'


class Conversation(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='conversations')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='conversations', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Диалог: {self.buyer} и {self.seller}'


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Сообщение от {self.sender}'
