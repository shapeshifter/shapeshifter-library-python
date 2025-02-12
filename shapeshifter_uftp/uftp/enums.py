from enum import StrEnum


class AcceptedDisputed(StrEnum):
    ACCEPTED = "Accepted"
    DISPUTED = "Disputed"


class AcceptedRejected(StrEnum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class AvailableRequested(StrEnum):
    AVAILABLE = "Available"
    REQUESTED = "Requested"


class RedispatchBy(StrEnum):
    AGR = "AGR"
    DSO = "DSO"

class UsefRole(StrEnum):
    AGR = "AGR"
    CRO = "CRO"
    DSO = "DSO"
