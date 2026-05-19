from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from marketplace.models import Conversation, Listing, Message, Order


class Command(BaseCommand):
    help = 'Создаёт демонстрационные данные для защиты проекта.'

    def handle(self, *args, **options):
        artist1, _ = User.objects.get_or_create(username='artist1', defaults={'email': 'artist1@example.com'})
        artist1.set_password('demo12345')
        artist1.save()
        artist1.profile.nickname = 'Pixel Raven'
        artist1.profile.about = 'Рисую выразительные стикер-паки для Telegram-каналов и личных блогов.'
        artist1.profile.portfolio_url = 'https://example.com/pixel-raven'
        artist1.profile.save()

        artist2, _ = User.objects.get_or_create(username='artist2', defaults={'email': 'artist2@example.com'})
        artist2.set_password('demo12345')
        artist2.save()
        artist2.profile.nickname = 'Emoji Forge'
        artist2.profile.about = 'Создаю эмоджи-паки, реакции и маленькие иконки.'
        artist2.profile.save()

        buyer, _ = User.objects.get_or_create(username='buyer1', defaults={'email': 'buyer1@example.com'})
        buyer.set_password('demo12345')
        buyer.save()
        buyer.profile.nickname = 'Заказчик канала'
        buyer.profile.about = 'Ищу художников для оформления Telegram-канала.'
        buyer.profile.save()

        l1, _ = Listing.objects.get_or_create(
            seller=artist1,
            category=Listing.Category.STICKERS,
            defaults={'title': 'Авторский стикер-пак для Telegram', 'description': 'Нарисую набор из 10 стикеров в едином стиле.', 'price': 3500, 'deadline_days': 7, 'views_count': 12},
        )
        l2, _ = Listing.objects.get_or_create(
            seller=artist2,
            category=Listing.Category.EMOJI,
            defaults={'title': 'Эмоджи-пак для сообщества', 'description': 'Сделаю 12 эмоджи для реакций и оформления чата.', 'price': 2400, 'deadline_days': 5, 'views_count': 21},
        )
        order, _ = Order.objects.get_or_create(listing=l1, buyer=buyer, seller=artist1, defaults={'price': l1.price, 'comment': 'Нужны стикеры для книжного Telegram-канала.'})
        conversation, _ = Conversation.objects.get_or_create(buyer=buyer, seller=artist1, listing=l1, defaults={'order': order})
        if not Message.objects.filter(conversation=conversation).exists():
            Message.objects.create(conversation=conversation, sender=buyer, text='Здравствуйте. Можно сделать стикеры в книжной тематике?')
            Message.objects.create(conversation=conversation, sender=artist1, text='Да, пришлите описание персонажа и желаемые эмоции.')
        self.stdout.write(self.style.SUCCESS('Демо-данные созданы. Логины: artist1, artist2, buyer1. Пароль: demo12345'))
