from django.urls import path
from trading.views.trade import TradeOfferCreateView, TradeOfferUpdateView, TradeOfferHistoryView, InventoryView

urlpatterns = [
    path("trade-offer/", TradeOfferCreateView.as_view(), name="trade-offer-create"),
    path("trade-offer/<int:trade_offer_id>/", TradeOfferUpdateView.as_view(), name="trade-offer-update"),
    path("trade-offer/history/", TradeOfferHistoryView.as_view(), name="trade-offer-history"),
    path("inventory/<int:user_id>/", InventoryView.as_view(), name="inventory-view"),
]