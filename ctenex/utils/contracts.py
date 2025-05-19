import httpx
from loguru import logger

from ctenex.domain.exceptions import InvalidContractIdError
from ctenex.domain.order_book.contract.schemas import ContractGetResponse


def validate_contract_id(contract_id: str, base_url: str) -> list[ContractGetResponse]:
    # Validate contract ID exists
    try:
        with httpx.Client() as client:
            response = client.get(f"{base_url}v1/stateless/supported-contracts")
            response.raise_for_status()
            supported_contracts = response.json()

            if contract_id not in [c["contract_id"] for c in supported_contracts]:
                logger.error(f"Error: Contract ID '{contract_id}' is not supported")
                raise InvalidContractIdError(
                    f"Contract ID '{contract_id}' is not supported"
                )
    except httpx.HTTPError as e:
        logger.error(f"Error validating contract ID: {str(e)}")
        raise InvalidContractIdError(f"Error validating contract ID: {str(e)}")

    # supported_contracts.
    return [ContractGetResponse(**c) for c in supported_contracts]
