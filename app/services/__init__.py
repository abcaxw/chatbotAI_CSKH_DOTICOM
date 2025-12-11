from fastapi.security import OAuth2PasswordBearer

import dlog
from coreAI.agents_workflow import TeamAgents

team_agent = None
try:
    team_agent = TeamAgents()
    dlog.dlog_i(f" ---INIT---: team_agent service successful")
except Exception as e:
    dlog.dlog_e(f" ---INIT---: team_agent service Unsuccessful {e}")
oauth2_scheme = None
try:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    dlog.dlog_i(f" ---INIT---: oauth2_scheme service successful")
except Exception as e:
    dlog.dlog_e(f" ---INIT---: oauth2_scheme service Unsuccessful {e}")
