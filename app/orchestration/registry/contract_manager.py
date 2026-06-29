from app.orchestration.state.state_contracts import (
    DEFAULT_CONTRACT,
    StateContract,
)


class ContractManager:

    def __init__(self):

        self._contracts = {
            "summary": StateContract(
                input_fields=["global_context"],
                output_fields=["summary"]
            ),
            "insights": StateContract(
                input_fields=["global_context"],
                output_fields=["insight"]
            ),
            "actions": StateContract(
                input_fields=["global_context"],
                output_fields=["actions"]
            ),
        }

    def resolve(self, function_name: str) -> StateContract:

        if function_name not in self._contracts:
            raise ValueError(f"Contract not found: {function_name}")

        return self._contracts[function_name]

    def validate_input(self, function_name: str, data: dict):

        contract = self.resolve(function_name)

        for field in contract.input_fields:
            if field not in data:
                raise ValueError(f"Missing input: {field}")

        return True

    def validate_output(self, function_name: str, output: dict):

        contract = self.resolve(function_name)

        for field in contract.output_fields:
            if field not in output:
                raise ValueError(f"Missing output: {field}")

        return True