import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
django.setup()

from accounts.models import VirtualCard

cards = VirtualCard.objects.all()
print(f'Total cards: {cards.count()}')
for i, card in enumerate(cards, 1):
    print(f'{i}. {card.cardholder_name:20} | {card.card_number} | Status: {card.status}')
