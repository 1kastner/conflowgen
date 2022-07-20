from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository

#: This mode of transport distribution is based on the report
#: :cite:p:`isl2015umschlagpotenzial`.
#: The exact data for transshipment and hinterland share is taken from page 22, Figure 12
#: "Containerumschlag des Hafens Hamburg in TEU / Marktsegment 2013".
#: The modal split of the hinterland is updated based on the figures presented by
#: :cite:t:`hafenhamburg2020modalsplit`.
#: After those adaptions, still there were several imbalances.
#: Thus, some traffic was shifted from deep sea vessels to feeders by adding/subtracting some constants.
#: In summary, this is an educated guess based on several sources.
DEFAULT_MODE_OF_TRANSPORT_DISTRIBUTION = {
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


def seed():
    repository = ModeOfTransportDistributionRepository()
    repository.set_mode_of_transport_distributions(DEFAULT_MODE_OF_TRANSPORT_DISTRIBUTION)
