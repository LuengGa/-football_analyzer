# Re-export for backward compatibility
from src.core.models.ticket_schema import LotteryTicket, TicketLeg

__all__ = ["LotteryTicket", "TicketLeg"]
