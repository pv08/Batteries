class AgentResults:
    def __init__(self, storage: bool, day: int, hour: int):
        self.storage=storage
        self.day=day
        self.hour=hour



class CommunitiesResults:
    def __init__(self, storage: bool, day: int, hour: int):
        self.storage=storage
        self.day=day
        self.hour=hour


class OptResults:
    def __init__(self, storage: bool, day: int, hour: int):
        self.storage=storage
        self.day=day
        self.hour=hour


class OptLogger:
    def __init__(self, storage: bool, day: int, hour: int, fob, solver_status, condition, opt_model, results):
        self.storage = storage
        self.day = day
        self.hour = hour
        self.fob = fob
        self.solver_status = solver_status
        self.condition = condition
        self.opt_model = opt_model
        self.results = results