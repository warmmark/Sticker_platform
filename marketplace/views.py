from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ListingForm, MessageForm, OrderForm, OrderStatusForm, ProfileForm, RegisterForm
from .models import Conversation, Favorite, Listing, Message, Order


def home(request):
    latest_listings = Listing.objects.filter(is_active=True)[:6]
    popular_listings = Listing.objects.filter(is_active=True).annotate(fav_count=Count('favorites')).order_by('-fav_count', '-views_count')[:6]
    return render(request, 'marketplace/home.html', {'latest_listings': latest_listings, 'popular_listings': popular_listings})


def catalog(request):
    listings = Listing.objects.filter(is_active=True).select_related('seller', 'seller__profile')
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(seller__username__icontains=query) | Q(seller__profile__nickname__icontains=query))
    if category in [Listing.Category.STICKERS, Listing.Category.EMOJI]:
        listings = listings.filter(category=category)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)

    if sort == 'price':
        listings = listings.order_by('price')
    elif sort == '-price':
        listings = listings.order_by('-price')
    elif sort == 'popular':
        listings = listings.annotate(fav_count=Count('favorites')).order_by('-fav_count', '-views_count')
    else:
        listings = listings.order_by('-created_at')

    return render(request, 'marketplace/catalog.html', {'listings': listings, 'query': query, 'category': category, 'sort': sort})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing.objects.select_related('seller', 'seller__profile'), pk=pk, is_active=True)
    listing.views_count += 1
    listing.save(update_fields=['views_count'])
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, listing=listing).exists()
    return render(request, 'marketplace/listing_detail.html', {'listing': listing, 'is_favorite': is_favorite})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация выполнена.')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'marketplace/profile.html', {'form': form})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user)
    return render(request, 'marketplace/my_listings.html', {'listings': listings})


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            if listing.is_active and Listing.objects.filter(seller=request.user, category=listing.category, is_active=True).exists():
                form.add_error('category', 'У вас уже есть активное объявление в этой категории.')
            else:
                listing.save()
                messages.success(request, 'Объявление создано.')
                return redirect('my_listings')
    else:
        form = ListingForm()
    return render(request, 'marketplace/listing_form.html', {'form': form, 'title': 'Создание объявления'})


@login_required
def listing_update(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            updated = form.save(commit=False)
            conflict = Listing.objects.filter(seller=request.user, category=updated.category, is_active=True).exclude(pk=listing.pk).exists()
            if updated.is_active and conflict:
                form.add_error('category', 'У вас уже есть активное объявление в этой категории.')
            else:
                updated.save()
                messages.success(request, 'Объявление обновлено.')
                return redirect('my_listings')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'marketplace/listing_form.html', {'form': form, 'title': 'Редактирование объявления'})


@login_required
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Объявление удалено.')
        return redirect('my_listings')
    return render(request, 'marketplace/confirm_delete.html', {'object': listing, 'back_url': 'my_listings'})


@login_required
def toggle_favorite(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    favorite = Favorite.objects.filter(user=request.user, listing=listing).first()
    if favorite:
        favorite.delete()
        messages.info(request, 'Объявление удалено из избранного.')
    else:
        Favorite.objects.create(user=request.user, listing=listing)
        messages.success(request, 'Объявление добавлено в избранное.')
    return redirect('listing_detail', pk=pk)


@login_required
def favorites(request):
    favorites_qs = Favorite.objects.filter(user=request.user).select_related('listing', 'listing__seller')
    return render(request, 'marketplace/favorites.html', {'favorites': favorites_qs})


@login_required
def create_order(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    if listing.seller == request.user:
        messages.error(request, 'Нельзя оформить заказ на собственное объявление.')
        return redirect('listing_detail', pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.listing = listing
            order.buyer = request.user
            order.seller = listing.seller
            order.price = listing.price
            order.save()
            conversation, _ = Conversation.objects.get_or_create(buyer=request.user, seller=listing.seller, listing=listing, defaults={'order': order})
            if not conversation.order:
                conversation.order = order
                conversation.save(update_fields=['order'])
            messages.success(request, 'Заказ создан.')
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
    return render(request, 'marketplace/order_form.html', {'form': form, 'listing': listing})


@login_required
def orders(request):
    active_statuses = [Order.Status.CREATED, Order.Status.ACCEPTED, Order.Status.IN_PROGRESS, Order.Status.WAITING_APPROVAL]
    active_orders = Order.objects.filter(Q(buyer=request.user) | Q(seller=request.user), status__in=active_statuses).select_related('listing', 'buyer', 'seller')
    archive_orders = Order.objects.filter(Q(buyer=request.user) | Q(seller=request.user)).exclude(status__in=active_statuses).select_related('listing', 'buyer', 'seller')
    return render(request, 'marketplace/orders.html', {'active_orders': active_orders, 'archive_orders': archive_orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('listing', 'buyer', 'seller'), Q(buyer=request.user) | Q(seller=request.user), pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус заказа обновлён.')
            return redirect('order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'marketplace/order_detail.html', {'order': order, 'form': form})


@login_required
def start_conversation(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    if listing.seller == request.user:
        messages.error(request, 'Нельзя начать диалог с самим собой.')
        return redirect('listing_detail', pk=pk)
    conversation, _ = Conversation.objects.get_or_create(buyer=request.user, seller=listing.seller, listing=listing)
    return redirect('conversation_detail', pk=conversation.pk)


@login_required
def conversations(request):
    qs = Conversation.objects.filter(Q(buyer=request.user) | Q(seller=request.user)).select_related('buyer', 'seller', 'listing', 'order')
    return render(request, 'marketplace/conversations.html', {'conversations': qs})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation.objects.select_related('buyer', 'seller', 'listing', 'order'), Q(buyer=request.user) | Q(seller=request.user), pk=pk)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conversation
            msg.sender = request.user
            msg.save()
            return redirect('conversation_detail', pk=pk)
    else:
        form = MessageForm()
    return render(request, 'marketplace/conversation_detail.html', {'conversation': conversation, 'form': form})
