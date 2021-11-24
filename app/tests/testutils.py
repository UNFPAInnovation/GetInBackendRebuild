
def generate_girl_json(last_name, year, user_id):
    return {
        "GetInMapGirlBundibugyo17_chew": {
            "GirlDemographic": [
                {
                    "FirstName": [
                        "MukuluGirlTest"
                    ],
                    "LastName": [
                        last_name
                    ],
                    "GirlsPhoneNumber": [
                        "0779281444"
                    ],
                    "DOB": [
                        "{year}-02-26".format(year=year)
                    ]
                }
            ],
            "GirlDemographic2": [
                {
                    "NextOfKinNumber": [
                        "0779281822"
                    ]
                }
            ],
            "GirlLocation": [
                {
                    "county": [
                        "BUGHENDERA_COUNTY"
                    ],
                    "subcounty": [
                        "SINDILA"
                    ],
                    "parish": [
                        "NYANKONDA"
                    ],
                    "village": [
                        "BULYATA_II"
                    ]
                }
            ],
            "Observations3": [
                {
                    "marital_status": [
                        "married"
                    ],
                    "education_level": [
                        "primary_level"
                    ],
                    "MenstruationDate": [
                        "2020-02-28"
                    ]
                }
            ],
            "Observations1": [
                {
                    "bleeding": [
                        "no"
                    ],
                    "fever": [
                        "yes"
                    ]
                }
            ],
            "Observations2": [
                {
                    "swollenfeet": [
                        "no"
                    ],
                    "blurred_vision": [
                        "no"
                    ]
                }
            ],
            "EmergencyCall": [
                ""
            ],
            "ANCAppointmentPreviousGroup": [
                {
                    "AttendedANCVisit": [
                        "no"
                    ]
                }
            ],
            "ContraceptiveGroup": [
                {
                    "UsedContraceptives": [
                        "no"
                    ],
                    "ReasonNoContraceptives": [
                        "None"
                    ]
                }
            ],
            "VouncherCardGroup": [
                {
                    "VoucherCard": [
                        "no"
                    ]
                }
            ],
            "meta": [
                {
                    "instanceID": [
                        "uuid:21a505a9-2d17-4fed-a3ad-183343227eb3"
                    ]
                }
            ]
        },
        "form_meta_data": {
            "GIRL_ID": "0",
            "USER_ID": user_id
        }
    }


