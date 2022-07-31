from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport

example_container_dwell_time_distribution = {
    ModeOfTransport.truck:
        {
            ModeOfTransport.truck:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 451.2,
                            'variance': 1353.6,
                            'maximum_number_of_hours': 2256.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 170.4,
                            'variance': 511.2,
                            'maximum_number_of_hours': 852,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 170.4,
                            'variance': 511.2,
                            'maximum_number_of_hours': 852,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 170.4,
                            'variance': 511.2,
                            'maximum_number_of_hours': 852,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.train:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 276.0,
                            'variance': 828.0,
                            'maximum_number_of_hours': 1380.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 40.8,
                            'variance': 122.4,
                            'maximum_number_of_hours': 204.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 40.8,
                            'variance': 122.4,
                            'maximum_number_of_hours': 204.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 40.8,
                            'variance': 122.4,
                            'maximum_number_of_hours': 204.0,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.feeder:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 312.0,
                            'variance': 936.0,
                            'maximum_number_of_hours': 1560.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 85.92,
                            'variance': 257.76,
                            'maximum_number_of_hours': 429.6,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 85.92,
                            'variance': 257.76,
                            'maximum_number_of_hours': 429.6,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 85.92,
                            'variance': 257.76,
                            'maximum_number_of_hours': 429.6,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.deep_sea_vessel:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 321.6,
                            'variance': 964.8,
                            'maximum_number_of_hours': 1608.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 156.0,
                            'variance': 468.0,
                            'maximum_number_of_hours': 780.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 156.0,
                            'variance': 468.0,
                            'maximum_number_of_hours': 780.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 156.0,
                            'variance': 468.0,
                            'maximum_number_of_hours': 780.0,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.barge:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 177.6,
                            'variance': 532.8,
                            'maximum_number_of_hours': 888,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        }
                }
        }, ModeOfTransport.train:
        {
            ModeOfTransport.truck:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 228.0,
                            'variance': 684.0,
                            'maximum_number_of_hours': 1140.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 69.6,
                            'variance': 208.8,
                            'maximum_number_of_hours': 348.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 69.6,
                            'variance': 208.8,
                            'maximum_number_of_hours': 348.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 69.6,
                            'variance': 208.8,
                            'maximum_number_of_hours': 348.0,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.train:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 199.2,
                            'variance': 597.6,
                            'maximum_number_of_hours': 996.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 288,
                            'variance': 864, 'maximum_number_of_hours': 1440,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 288,
                            'variance': 864,
                            'maximum_number_of_hours': 1440,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 288,
                            'variance': 864,
                            'maximum_number_of_hours': 1440,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.feeder:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 384,
                            'variance': 1152,
                            'maximum_number_of_hours': 1920,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 98.4,
                            'variance': 295.2,
                            'maximum_number_of_hours': 492,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 98.4,
                            'variance': 295.2,
                            'maximum_number_of_hours': 492,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 98.4,
                            'variance': 295.2,
                            'maximum_number_of_hours': 492,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.deep_sea_vessel:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 307.2,
                            'variance': 921.6,
                            'maximum_number_of_hours': 1536.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 160.8,
                            'variance': 482.4,
                            'maximum_number_of_hours': 804.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 160.8,
                            'variance': 482.4,
                            'maximum_number_of_hours': 804.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 160.8,
                            'variance': 482.4,
                            'maximum_number_of_hours': 804.0,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.barge:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 194.4,
                            'variance': 583.2,
                            'maximum_number_of_hours': 972,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 350.4,
                            'variance': 1051.2,
                            'maximum_number_of_hours': 1752.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 350.4,
                            'variance': 1051.2,
                            'maximum_number_of_hours': 1752.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 350.4,
                            'variance': 1051.2,
                            'maximum_number_of_hours': 1752.0,
                            'minimum_number_of_hours': 0
                        }
                }
        },
    ModeOfTransport.feeder:
        {
            ModeOfTransport.truck:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 326.4,
                            'variance': 979.2,
                            'maximum_number_of_hours': 1632.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 74.4,
                            'variance': 223.2,
                            'maximum_number_of_hours': 372.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 74.4,
                            'variance': 223.2,
                            'maximum_number_of_hours': 372.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 74.4,
                            'variance': 223.2,
                            'maximum_number_of_hours': 372.0,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.train:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 326.4,
                            'variance': 979.2,
                            'maximum_number_of_hours': 1632.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 96,
                            'variance': 288,
                            'maximum_number_of_hours': 480,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 96,
                            'variance': 288,
                            'maximum_number_of_hours': 480,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 96,
                            'variance': 288,
                            'maximum_number_of_hours': 480,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.feeder:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 254.4,
                            'variance': 763.1999999999999,
                            'maximum_number_of_hours': 1272.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 91.2,
                            'variance': 273.6,
                            'maximum_number_of_hours': 456,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 91.2,
                            'variance': 273.6,
                            'maximum_number_of_hours': 456,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 91.2,
                            'variance': 273.6,
                            'maximum_number_of_hours': 456,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.deep_sea_vessel:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 350.4,
                            'variance': 1051.2,
                            'maximum_number_of_hours': 1752.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 199.2,
                            'variance': 597.6,
                            'maximum_number_of_hours': 996.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 199.2,
                            'variance': 597.6,
                            'maximum_number_of_hours': 996.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 199.2,
                            'variance': 597.6,
                            'maximum_number_of_hours': 996.0,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.barge:
                {
                    StorageRequirement.empty: {
                        'distribution_name': 'lognormal',
                        'average_number_of_hours': 196.8,
                        'variance': 590.4,
                        'maximum_number_of_hours': 984,
                        'minimum_number_of_hours': 3
                    },
                    StorageRequirement.standard: {
                        'distribution_name': 'lognormal',
                        'average_number_of_hours': 57.6,
                        'variance': 172.8,
                        'maximum_number_of_hours': 288.0,
                        'minimum_number_of_hours': 3
                    },
                    StorageRequirement.reefer: {
                        'distribution_name': 'lognormal',
                        'average_number_of_hours': 57.6,
                        'variance': 172.8,
                        'maximum_number_of_hours': 288.0,
                        'minimum_number_of_hours': 3
                    },
                    StorageRequirement.dangerous_goods: {
                        'distribution_name': 'lognormal',
                        'average_number_of_hours': 57.6,
                        'variance': 172.8,
                        'maximum_number_of_hours': 288.0,
                        'minimum_number_of_hours': 3
                    }
                }
        },
    ModeOfTransport.deep_sea_vessel:
        {
            ModeOfTransport.truck:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 292.8,
                            'variance': 878.4,
                            'maximum_number_of_hours': 1464,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3},
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.train:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 264,
                            'variance': 792,
                            'maximum_number_of_hours': 1320,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {

                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 72,
                            'variance': 216,
                            'maximum_number_of_hours': 360,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.feeder:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 336,
                            'variance': 1008,
                            'maximum_number_of_hours': 1680,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 103.2,
                            'variance': 309.6,
                            'maximum_number_of_hours': 516.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 103.2,
                            'variance': 309.6,
                            'maximum_number_of_hours': 516.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 103.2,
                            'variance': 309.5,
                            'maximum_number_of_hours': 516.0,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.deep_sea_vessel:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 664.8,
                            'variance': 1994.4,
                            'maximum_number_of_hours': 3324.0,
                            'minimum_number_of_hours': 3},
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 223.2,
                            'variance': 669.6,
                            'maximum_number_of_hours': 1116.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 223.2,
                            'variance': 669.6,
                            'maximum_number_of_hours': 1116.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 223.2,
                            'variance': 669.6,
                            'maximum_number_of_hours': 1116.0,
                            'minimum_number_of_hours': 3
                        }
                },
            ModeOfTransport.barge:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 268.8,
                            'variance': 806.4,
                            'maximum_number_of_hours': 1344,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 60.0,
                            'variance': 180.0,
                            'maximum_number_of_hours': 300.0,
                            'minimum_number_of_hours': 3
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 60.0,
                            'variance': 180.0,
                            'maximum_number_of_hours': 300.0,
                            'minimum_number_of_hours': 3},
                    StorageRequirement.dangerous_goods:
                        {

                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 60.0,
                            'variance': 180.0,
                            'maximum_number_of_hours': 300.0,
                            'minimum_number_of_hours': 3
                        }
                }
        },
    ModeOfTransport.barge:
        {
            ModeOfTransport.truck:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 230.4,
                            'variance': 691.2,
                            'maximum_number_of_hours': 1152.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 192,
                            'variance': 576,
                            'maximum_number_of_hours': 960,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 192,
                            'variance': 576,
                            'maximum_number_of_hours': 960,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 192,
                            'variance': 576,
                            'maximum_number_of_hours': 960,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.train:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 196.8,
                            'variance': 590.4,
                            'maximum_number_of_hours': 984,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 240,
                            'variance': 720,
                            'maximum_number_of_hours': 1200,
                            'minimum_number_of_hours': 0
                        }
                },
            ModeOfTransport.feeder:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 345.6,
                            'variance': 1036.8,
                            'maximum_number_of_hours': 1728.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 100.8,
                            'variance': 302.4,
                            'maximum_number_of_hours': 504.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 100.8,
                            'variance': 302.40000000000003,
                            'maximum_number_of_hours': 504.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 100.8,
                            'variance': 302.4,
                            'maximum_number_of_hours': 504.0,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.deep_sea_vessel:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 422.40000000000003,
                            'variance': 1267.2,
                            'maximum_number_of_hours': 2112.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 163.2,
                            'variance': 489.6,
                            'maximum_number_of_hours': 816.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 163.2,
                            'variance': 489.6,
                            'maximum_number_of_hours': 816.0,
                            'minimum_number_of_hours': 12
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 163.2,
                            'variance': 489.6,
                            'maximum_number_of_hours': 816.0,
                            'minimum_number_of_hours': 12
                        }
                },
            ModeOfTransport.barge:
                {
                    StorageRequirement.empty:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 278.4,
                            'variance': 835.1999999999999,
                            'maximum_number_of_hours': 1392.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.standard:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 108.0,
                            'variance': 324.0,
                            'maximum_number_of_hours': 540.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.reefer:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 108.0,
                            'variance': 324.0,
                            'maximum_number_of_hours': 540.0,
                            'minimum_number_of_hours': 0
                        },
                    StorageRequirement.dangerous_goods:
                        {
                            'distribution_name': 'lognormal',
                            'average_number_of_hours': 108.0,
                            'variance': 324.0,
                            'maximum_number_of_hours': 540.0,
                            'minimum_number_of_hours': 0
                        }
                }
        }
}
