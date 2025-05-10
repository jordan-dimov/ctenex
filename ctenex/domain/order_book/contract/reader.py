from ctenex.core.data_access.reader import GenericReader
from ctenex.domain.entities import Contract


class ContractsReader(GenericReader[Contract]):
    """Reader for Book contracts."""

    model = Contract


contracts_reader = ContractsReader()
