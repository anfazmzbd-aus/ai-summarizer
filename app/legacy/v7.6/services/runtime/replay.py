from copy import deepcopy


class ReplayEngine:

    @staticmethod
    def restore(snapshot):

        return deepcopy(
            snapshot
        )