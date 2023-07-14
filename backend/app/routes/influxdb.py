from typing import Any
from typing import Dict

from flask import Blueprint
from flask import jsonify
from flask import request
from loguru import logger

from app.services.InfluxDB.alerts import InfluxDBAlertsService
from app.services.InfluxDB.checks import InfluxDBChecksService

bp = Blueprint("influxdb", __name__)


@bp.route("/influxdb/checks", methods=["GET"])
def get_checks() -> jsonify:
    """
    Endpoint to retrive list of InfluxDB checks.
    Requires API token of `admin` user.

    Returns:
        jsonify: A JSON response containing the list of all checks from InfluxDB.

    """
    logger.info("Received request to get all InfluxDB checks")
    service = InfluxDBChecksService.from_connector_details("InfluxDB")
    checks = service.collect_checks()
    return jsonify(checks)


@bp.route("/influxdb/checks/<check_id>", methods=["GET"])
def get_check_query(check_id: str) -> jsonify:
    """
    Endpoint to retrive query of InfluxDB check.
    Requires API token of `admin` user.

    Returns:
        jsonify: A JSON response containing the query of the check from InfluxDB.

    """
    logger.info("Received request to get InfluxDB check query")
    service = InfluxDBChecksService.from_connector_details("InfluxDB")
    check_query = service.collect_check_query(check_id)
    return jsonify(check_query)

@bp.route("/influxdb/alerts", methods=["GET"])
def get_alerts() -> jsonify:
    """
    Endpoint to list all alerts from the `influxdb_alerts` table.

    Returns:
        jsonify: A JSON response containing the list of all alerts from InfluxDB.
    """
    logger.info("Received request to get all InfluxDB alerts")
    service = InfluxDBAlertsService.from_connector_details("InfluxDB")
    alerts = service.collect_alerts()
    return jsonify(alerts)

@bp.route("/influxdb/alert", methods=["POST"])
def put_alert() -> jsonify:
    """
    Endpoint to store alert in the `influxdb_alerts` table.
    Invoked by the InfluxDB alert webhook which is configured in the InfluxDB UI.

    Returns:
        jsonify: A JSON response containing if the alert was stored successfully.
    """
    logger.info("Received request to store InfluxDB alert")
    data: Dict[str, Any] = request.get_json()
    logger.info(data)
    service = InfluxDBAlertsService.from_connector_details("InfluxDB")

    try:
        check_name, message = service.validate_payload(data=data)
        service.store_alerts(check_name=check_name, message=message)
        return jsonify({"message": "Successfully stored alert.", "success": True}), 200
    except Exception as e:
        logger.error(f"Received invalid payload. {e}")
        return jsonify({"message": "Invalid payload.", "success": False}), 400