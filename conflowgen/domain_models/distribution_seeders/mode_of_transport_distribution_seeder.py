from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


def seed():
    """
    Seeds the database with some initial values for the modal split.

    This mode of transport distribution is based on the report
    "Prognose des Umschlagpotenzials und des Modal Splits des Hamburger Hafens für die Jahre 2020, 2025 und 2030"
    as available at
    https://www.hamburg-port-authority.de/fileadmin/user_upload/Endbericht_Potenzialprognose_Mai2015_5.pdf

    The exact data for transshipment and hinterland share is taken from page 22, Figure 12
    "Containerumschlag des Hafens Hamburg in TEU / Marktsegment 2013"

    For the modal split in the hinterland, the current percentage values are taken from
    https://www.hafen-hamburg.de/de/statistiken/modal-split/

    After those adaptions, still there were several imbalances. Thus, some traffic was shifted from deep sea vessels to
    feeders by adding/subtracting some constants.
    """

    repository = ModeOfTransportDistributionRepository()

    mode_of_transport_distribution = {
        ModeOfTransport.truck: {
            ModeOfTransport.truck: 0,
            ModeOfTransport.train: 0,
            ModeOfTransport.barge: 0,
            ModeOfTransport.feeder: 0.8 / (0.8 + 4.6) + 0.15,
            ModeOfTransport.deep_sea_vessel: 4.6 / (0.8 + 4.6) - 0.15
        },
        ModeOfTransport.train: {
            ModeOfTransport.truck: 0,
            ModeOfTransport.train: 0,
            ModeOfTransport.barge: 0,
            ModeOfTransport.feeder: 0.8 / (0.8 + 4.6) + 0.15,
            ModeOfTransport.deep_sea_vessel: 4.6 / (0.8 + 4.6) - 0.15
        },
        ModeOfTransport.barge: {
            ModeOfTransport.truck: 0,
            ModeOfTransport.train: 0,
            ModeOfTransport.barge: 0,
            ModeOfTransport.feeder: 0.8 / (0.8 + 4.6),
            ModeOfTransport.deep_sea_vessel: 4.6 / (0.8 + 4.6)
        },
        ModeOfTransport.feeder: {
            ModeOfTransport.truck: 0.8 / (0.8 + 1.9) * 0.502,
            ModeOfTransport.train: 0.8 / (0.8 + 1.9) * 0.47,
            ModeOfTransport.barge: 0.8 / (0.8 + 1.9) * 0.0028,
            ModeOfTransport.feeder: 0,
            ModeOfTransport.deep_sea_vessel: 1.9 / (0.8 + 1.9)
        },
        ModeOfTransport.deep_sea_vessel: {
            ModeOfTransport.truck: 4.6 / (4.6 + 1.9) * 0.502,
            ModeOfTransport.train: 4.6 / (4.6 + 1.9) * 0.47,
            ModeOfTransport.barge: 4.6 / (4.6 + 1.9) * 0.0028,
            ModeOfTransport.feeder: 1.9 / (4.6 + 1.9),
            ModeOfTransport.deep_sea_vessel: 0
        }
    }

    repository.set_mode_of_transport_distributions(mode_of_transport_distribution)
