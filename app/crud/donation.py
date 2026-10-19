from app.crud.base import CRUDBase
from app.models import Donation
from app.schemas.donation import DonationCreate


class CRUDDonation(CRUDBase[Donation, DonationCreate]):
    """Операции с пожертвованиями."""


donation_crud = CRUDDonation(Donation)
