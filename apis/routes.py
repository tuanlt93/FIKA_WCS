"""
TODO: Import active url resources here
"""
from apis.api_base import api
from apis.DAL.DWS_api import DWSHeartBeat, DWSResult
from apis.DAL.monitor_agv_api import MonitorMission

from apis.DAL.pda_api import (
    PDA_Input,
    PDA_Pallet_Empty_Input,
    ConfirmQtyPalletCarton,
    GetCartonStateInputError,
    CreateInspection,
    CreateCorrection,
    PdaPrint,
    PdaPrintPresent,
    PdaQuarantined,
    PDA_Call_AGV
)

api.addClassResource(PDA_Input)
api.addClassResource(PDA_Pallet_Empty_Input)
api.addClassResource(ConfirmQtyPalletCarton)
api.addClassResource(GetCartonStateInputError)
api.addClassResource(CreateInspection)
api.addClassResource(CreateCorrection)
api.addClassResource(PdaPrint) # -v
api.addClassResource(PdaPrintPresent) # -v
api.addClassResource(PdaQuarantined) # -v
api.addClassResource(PDA_Call_AGV)


api.addClassResource(DWSHeartBeat)
api.addClassResource(DWSResult)
api.addClassResource(MonitorMission)