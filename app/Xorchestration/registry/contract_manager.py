from typing import Dict

from app.orchestration.state.state_contracts import (
    StateContract,
)


class ContractManager:

    def __init__(self):

        self._contracts: Dict[
            str,
            StateContract
        ] = {}

    # -------------------------
    # Register
    # -------------------------

    def register(

        self,

        function_name: str,

        contract: StateContract,

    ):

        self._contracts[
            function_name
        ] = contract

    # -------------------------
    # Resolve
    # -------------------------

    def resolve(

        self,

        function_name: str,

    ) -> StateContract:

        if (
            function_name
            not in self._contracts
        ):

            raise ValueError(

                f"Contract not found: "

                f"{function_name}"

            )

        return self._contracts[
            function_name
        ]

    # -------------------------
    # Validate
    # -------------------------

    def validate_input(

        self,

        function_name,

        data,

    ):

        contract = (
            self.resolve(
                function_name
            )
        )

        contract.validate_input(
            data
        )

    def validate_output(

        self,

        function_name,

        data,

    ):

        contract = (
            self.resolve(
                function_name
            )
        )

        contract.validate_output(
            data
        )