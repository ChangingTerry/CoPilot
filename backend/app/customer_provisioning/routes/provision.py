from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.auth.utils import AuthHandler
from app.connectors.grafana.schema.dashboards import Office365Dashboard
from app.connectors.grafana.schema.dashboards import WazuhDashboard
from app.customer_provisioning.schema.provision import CustomerProvisionResponse
from app.customer_provisioning.schema.provision import CustomersMetaResponse
from app.customer_provisioning.schema.provision import CustomerSubsctipion
from app.customer_provisioning.schema.provision import GetDashboardsResponse
from app.customer_provisioning.schema.provision import GetSubscriptionsResponse
from app.customer_provisioning.schema.provision import ProvisionNewCustomer
from app.customer_provisioning.services.provision import provision_wazuh_customer
from app.db.db_session import get_db
from app.db.universal_models import Customers
from app.db.universal_models import CustomersMeta

customer_provisioning_router = APIRouter()


def get_available_dashboards():
    """
    Get a list of available dashboards.

    Returns:
        list: A list of available dashboards.

    Raises:
        HTTPException: If there is an error getting the available dashboards.
    """
    try:
        wazuh_dashboards = [dashboard.name for dashboard in WazuhDashboard]
        office365_dashboards = [dashboard.name for dashboard in Office365Dashboard]
        return wazuh_dashboards + office365_dashboards
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available dashboards: {e}",
        )


def get_available_subscriptions():
    """
    Retrieves a list of available subscriptions.

    Returns:
        list: A list of available subscriptions.

    Raises:
        HTTPException: If there is an error getting the available subscriptions.
    """
    try:
        return [subscription.value for subscription in CustomerSubsctipion]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available subscriptions: {e}",
        )


async def check_customer_exists(
    customer_code: str,
    session: AsyncSession = Depends(get_db),
) -> Customers:
    """
    Check if a customer exists in the database.

    Args:
        customer_code (str): The code of the customer to check.
        session (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Customers: The customer object if found.

    Raises:
        HTTPException: If the customer is not found in the database.
    """
    logger.info(f"Checking if customer {customer_code} exists")
    result = await session.execute(
        select(Customers).filter(Customers.customer_code == customer_code),
    )
    customer = result.scalars().first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer: {customer_code} not found. Please create the customer first.",
        )

    return customer


async def check_unique_ports(request: ProvisionNewCustomer, session: AsyncSession):
    """
    Ensures that the ports specified in the request are unique.

    Args:
        request: The request data containing the ports to check.
        session: The database session.

    Raises:
        HTTPException: If the ports are not unique.
    """
    ports = {
        "registration": request.wazuh_registration_port,
        "logs": request.wazuh_logs_port,
        "api": request.wazuh_api_port,
    }

    for port_type, port_value in ports.items():
        customer_meta = await get_customer_meta_by_port(port_value, session)
        if customer_meta:
            raise HTTPException(
                status_code=400,
                detail=f"Ports must be unique. {port_type.capitalize()} port {port_value} is already in use for customer {customer_meta.customer_code}.",
            )


async def get_customer_meta_by_port(port: int, session: AsyncSession):
    """
    Retrieves customer metadata based on the provided port.

    Args:
        port: The port to check.
        session: The database session.

    Returns:
        Customer metadata if a match is found, otherwise None.
    """
    result = await session.execute(
        select(CustomersMeta).filter(
            (CustomersMeta.customer_meta_wazuh_registration_port == port)
            | (CustomersMeta.customer_meta_wazuh_log_ingestion_port == port)
            | (CustomersMeta.customer_meta_wazuh_api_port == port),
        ),
    )
    return result.scalars().first()


@customer_provisioning_router.post(
    "/provision",
    response_model=CustomerProvisionResponse,
    description="Provision New Customer",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def provision_customer_route(
    request: ProvisionNewCustomer = Body(...),
    _customer: Customers = Depends(check_customer_exists),
    session: AsyncSession = Depends(get_db),
):
    """
    Provisions a new customer.

    Args:
        request (ProvisionNewCustomer): The request data for provisioning a new customer.
        _customer (Customers): The existing customer data.
        session (AsyncSession): The database session.

    Returns:
        CustomerProvisionResponse: The response data for the provisioned customer.
    """
    await check_unique_ports(request, session)
    logger.info("Provisioning new customer")
    customer_provision = await provision_wazuh_customer(request, session=session)
    return customer_provision


@customer_provisioning_router.get(
    "/provision/dashboards",
    response_model=GetDashboardsResponse,
    description="Return the list of dashboards available for provisioning",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_dashboards_route():
    """
    Get the list of dashboards available for provisioning.

    Returns:
        GetDashboardsResponse: The response containing the available dashboards.
    """
    logger.info("Getting list of dashboards")
    available_dashboards = get_available_dashboards()
    return GetDashboardsResponse(
        available_dashboards=available_dashboards,
        success=True,
        message="Dashboards retrieved successfully",
    )


@customer_provisioning_router.get(
    "/provision/subscriptions",
    response_model=GetSubscriptionsResponse,
    description="Return the list of subscriptions available for provisioning",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_subscriptions_route():
    """
    Get the list of subscriptions available for provisioning.

    Returns:
        GetSubscriptionsResponse: The response containing the available subscriptions.
    """
    logger.info("Getting list of subscriptions")
    available_subscriptions = get_available_subscriptions()
    return GetSubscriptionsResponse(
        available_subscriptions=available_subscriptions,
        success=True,
        message="Subscriptions retrieved successfully",
    )


# Get the customermeta based on the customer code
@customer_provisioning_router.get(
    "/provision/{customer_code}",
    response_model=CustomersMetaResponse,
    description="Get Customer Meta",
    dependencies=[Security(AuthHandler().require_any_scope("admin", "analyst"))],
)
async def get_customer_meta(
    customer_code: str,
    session: AsyncSession = Depends(get_db),
):
    """
    Retrieve customer meta data for a given customer code.

    Args:
        customer_code (str): The code of the customer to retrieve meta data for.
        session (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If customer meta data is not found for the given customer code.

    Returns:
        CustomersMetaResponse: The response containing the customer meta data.
    """
    logger.info(f"Getting customer meta for customer {customer_code}")
    result = await session.execute(
        select(CustomersMeta).filter(CustomersMeta.customer_code == customer_code),
    )
    customer_meta = result.scalars().first()

    if not customer_meta:
        raise HTTPException(
            status_code=404,
            detail=f"Customer meta not found for customer: {customer_code}. Please provision the customer first.",
        )

    return CustomersMetaResponse(
        message="Customer meta retrieved successfully",
        success=True,
        customer_meta=customer_meta,
    )
