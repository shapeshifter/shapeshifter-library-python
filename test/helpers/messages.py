from datetime import datetime, timezone
from uuid import uuid4

from xsdata.models.datatype import XmlDate

from shapeshifter_uftp.uftp import *

default_args = {
    "version": "3.0.0",
    "sender_domain": "agr.dev",
    "recipient_domain": "cro.dev",
    "time_stamp": datetime.now(timezone.utc).isoformat(),
    "message_id": str(uuid4()),
    "conversation_id": str(uuid4())
}

messages = [
    AgrPortfolioQuery(period=XmlDate(2023, 1, 1), **default_args),
    AgrPortfolioQueryResponse(
        dso_views=[
            AgrPortfolioQueryResponseDSOView(
                dso_portfolios=[
                    AgrPortfolioQueryResponseDSOPortfolio(
                        congestion_points=[
                            AgrPortfolioQueryResponseCongestionPoint(
                                connections=[
                                    AgrPortfolioQueryResponseConnection(
                                        entity_address="ean.210987654321"
                                    )
                                ],
                                entity_address="ean.123456789012",
                                mutex_offers_supported=True,
                                day_ahead_redispatch_by=RedispatchBy.AGR,
                                intraday_redispatch_by=RedispatchBy.AGR,
                            )
                        ],
                        dso_domain="dso.dev"
                    )
                ]
            )
        ],
        period=XmlDate(2023, 1, 1),
        agr_portfolio_query_message_id=str(uuid4()),
        **default_args
    ),
    AgrPortfolioUpdate(
        connections=[
            AgrPortfolioUpdateConnection(
                entity_address="ean.123456789012",
                start_period=XmlDate(2023, 1, 1)
            )
        ],
        **default_args
    ),
    AgrPortfolioUpdateResponse(agr_portfolio_update_message_id=str(uuid4()), **default_args),
    DPrognosis(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        isps=[
            DPrognosisISP(
                power=2,
                start=1,
                duration=1
            )
        ],
        revision=1,
        **default_args
    ),
    DPrognosisResponse(
        d_prognosis_message_id=str(uuid4()),
        **default_args,
    ),
    DsoPortfolioQuery(
        entity_address="ean.123456789012", period=XmlDate(2023, 5, 1), **default_args
    ),
    DsoPortfolioQueryResponse(
        congestion_point=DsoPortfolioQueryCongestionPoint(
            connections=[
                DsoPortfolioQueryConnection(
                    entity_address="ean.123456789012",
                    agr_domain="agr.dev"
                )
            ],
            entity_address="ean.123456789012"
        ),
        period=XmlDate(2023, 5, 1),
        dso_portfolio_query_message_id=str(uuid4()),
        **default_args,
    ),
    DsoPortfolioUpdate(
        congestion_points=[
            DsoPortfolioUpdateCongestionPoint(
                connections=[
                    DsoPortfolioUpdateConnection(
                        entity_address="ean.123456789012",
                        start_period=XmlDate(2023, 1, 1),
                        end_period=XmlDate(2023, 1, 1),
                    )
                ],
                entity_address="ean.123456789012",
                start_period=XmlDate(2023, 1, 1),
                end_period=XmlDate(2023, 1, 1),
                mutex_offers_supported=True,
                day_ahead_redispatch_by=RedispatchBy.AGR,
                intraday_redispatch_by=RedispatchBy.AGR,
            )
        ],
        **default_args
    ),
    DsoPortfolioUpdateResponse(
        dso_portfolio_update_message_id=str(uuid4()), **default_args
    ),
    FlexOffer(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        expiration_date_time=datetime.now(timezone.utc).isoformat(),
        offer_options=[
            FlexOfferOption(
                isps=[
                    FlexOfferOptionISP(
                        power=1,
                        start=1,
                        duration=1
                    )
                ],
                option_reference="MyOption",
                price=2.30,
                min_activation_factor=0.5
            )
        ],
        **default_args
    ),
    FlexOfferResponse(flex_offer_message_id=str(uuid4()), **default_args),
    FlexOfferRevocation(flex_offer_message_id=str(uuid4()), **default_args),
    FlexOfferRevocationResponse(flex_offer_revocation_message_id=str(uuid4()), **default_args),
    FlexOrder(
        isps=[FlexOrderISP(
            power=1,
            duration=1,
            start=1
        )],
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        flex_offer_message_id=str(uuid4()),
        contract_id=str(uuid4()),
        d_prognosis_message_id=str(uuid4()),
        baseline_reference=str(uuid4()),
        price=2.00,
        currency="EUR",
        order_reference=str(uuid4()),
        option_reference=str(uuid4()),
        activation_factor=0.5,
        **default_args
    ),
    FlexOrderResponse(
        flex_order_message_id=str(uuid4()),
        **default_args
    ),
    FlexRequest(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        isps=[
            FlexRequestISP(
                disposition=AvailableRequested.REQUESTED,
                min_power=0,
                max_power=10,
                start=1,
                duration=1,
            )
        ],
        revision=1,
        expiration_date_time=datetime.now(timezone.utc).isoformat(),
        contract_id=str(uuid4()),
        service_type="MyService",
        **default_args
    ),
    FlexReservationUpdate(
        isp_duration="PT15M",
        period=XmlDate(2023, 1, 1),
        congestion_point="ean.123456789012",
        isps=[
            FlexReservationUpdateISP(
                power=1,
                start=1,
                duration=1
            )
        ],
        contract_id=str(uuid4()),
        reference="MyReference",
        **default_args,
    ),
    FlexReservationUpdateResponse(
        flex_reservation_update_message_id=str(uuid4()),
        **default_args
    ),
    FlexSettlement(
        flex_order_settlements=[
            FlexOrderSettlement(
                isps=[
                    FlexOrderSettlementISP(
                        start=1,
                        duration=1,
                        baseline_power=1,
                        ordered_flex_power=1,
                        actual_power=1,
                        delivered_flex_power=1,
                        power_deficiency=1,
                    )
                ],
                period=XmlDate(2023, 1, 1),
                congestion_point="ean.123456789012",
                order_reference=str(uuid4()),
                contract_id=str(uuid4()),
                d_prognosis_message_id=str(uuid4()),
                baseline_reference=str(uuid4()),
                price=1.0,
                penalty=1.0,
                net_settlement=2.0,
            )
        ],
        contract_settlements=[
            ContractSettlement(
                periods=[
                    ContractSettlementPeriod(
                        isps=[
                            ContractSettlementISP(
                                start=1,
                                duration=1,
                                reserved_power=1,
                                requested_power=1,
                                available_power=1,
                                offered_power=1,
                                ordered_power=1,
                            )
                        ],
                        period=XmlDate(2023, 1, 1)
                    )
                ],
                contract_id=str(uuid4())
            )
        ],
        period_start=XmlDate(2023, 1, 1),
        period_end=XmlDate(2023, 5, 1),
        currency="EUR",
        **default_args,
    ),
    FlexSettlementResponse(
        flex_order_settlement_statuses=[
            FlexOrderSettlementStatus(
                order_reference=str(uuid4()),
                disposition=AcceptedDisputed.ACCEPTED,
                dispute_reason="My Reason",
            )
        ],
        flex_settlement_message_id=str(uuid4()),
        **default_args,
    ),
    FlexRequestResponse(
        flex_request_message_id=str(uuid4()),
        **default_args,
    ),
    Metering(
        profiles=[
            MeteringProfile(
                isps=[
                    MeteringISP(
                        start=1,
                        value=1
                    )
                ],
                profile_type=MeteringProfileEnum.POWER,
                unit=MeteringUnit.K_W,
            )
        ],
        revision=1,
        isp_duration="PT15M",
        time_zone="Europe/Amsterdam",
        currency="EUR",
        period=XmlDate(2023, 1, 1),
        ean="E1234567890123456",
        **default_args
    ),
    MeteringResponse(
        metering_message_id=str(uuid4()),
        **default_args
    ),

]

messages_by_type = {
    type(message): message for message in messages
}
