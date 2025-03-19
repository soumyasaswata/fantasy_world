from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trading.exceptions import TradeValidationError
from trading.serializers.trade import TradeOfferSerializer
from trading.services.trade_service import TradeService
from trading.models import TradeOffer, Inventory
from django.db.models import Q
from django.utils.dateparse import parse_date
from trading.serializers.inventory import InventorySerializer
from django.utils.timezone import make_aware
from datetime import datetime

class TradeOfferCreateView(CreateAPIView):
    serializer_class = TradeOfferSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender_id = serializer.validated_data["sender_id"]
        receiver_id = serializer.validated_data["receiver_id"]
        offered_items = request.data.get("offered_items", [])
        requested_items = request.data.get("requested_items", [])

        try:
            trade_offer = TradeService.create_trade_offer(sender_id, receiver_id, offered_items, requested_items)
            return Response({"trade_offer_id": trade_offer.id}, status=status.HTTP_201_CREATED)
        except TradeValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TradeOfferUpdateView(APIView):
    """
    Allows users to accept or reject a trade offer.
    """

    def patch(self, request, trade_offer_id):
        receiver_id = request.data.get("receiver_id")
        action = request.data.get("action")

        if not receiver_id:
            return Response({"error": "Receiver ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if action not in ["ACCEPT", "REJECT"]:
            return Response({"error": "Invalid action. Use 'ACCEPT' or 'REJECT'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trade_offer = TradeService.process_trade_offer(trade_offer_id, receiver_id, action)
            return Response({"trade_offer_id": trade_offer.id, "status": trade_offer.get_status_display()}, status=status.HTTP_200_OK)
        except TradeValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class TradeOfferHistoryView(APIView):
    """
    Fetch trade history with optional filters.
    """

    def get(self, request):
        user_id = request.query_params.get("user_id")
        status_filter = request.query_params.get("status")
        sent_or_received = request.query_params.get("type")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        trade_offers = TradeOffer.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id))

        if sent_or_received:
            if sent_or_received.lower() == "sent":
                trade_offers = trade_offers.filter(sender_id=user_id)
            elif sent_or_received.lower() == "received":
                trade_offers = trade_offers.filter(receiver_id=user_id)
            else:
                return Response({"error": "Invalid type parameter"}, status=400)

        if status_filter:
            trade_offers = trade_offers.filter(status=status_filter)

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                start_date = make_aware(datetime.combine(start_date, datetime.min.time()))
                trade_offers = trade_offers.filter(created_at__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                end_date = make_aware(datetime.combine(end_date, datetime.max.time()))
                trade_offers = trade_offers.filter(created_at__lte=end_date)

        serialized_data = TradeOfferSerializer(trade_offers, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)


class InventoryView(ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Inventory.objects.filter(user_id=user_id)