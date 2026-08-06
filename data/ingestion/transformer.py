from typing import Dict, List

from graph.schema.nodes import CORE_NODES
from graph.schema.relationships import CORE_RELATIONSHIPS


class GraphTransformer:

    # NODE TRANSFORMATIONS
    @staticmethod
    def transform_company(record: Dict) -> Dict:

        company_uri = record.get("company", "")
        company_id = company_uri.split("/")[-1]

        return {
            "label": CORE_NODES["COMPANY"],
            "company_id": company_id,
            "name": record.get("companyLabel")
        }

    @staticmethod
    def transform_country(record: Dict) -> Dict:

        country_uri = record.get("country", "")
        country_code = country_uri.split("/")[-1]

        return {
            "label": CORE_NODES["COUNTRY"],
            "country_code": country_code,
            "name": record.get("countryLabel")
        }

    @staticmethod
    def transform_port(record: Dict) -> Dict:

        port_uri = record.get("port", "")
        port_id = port_uri.split("/")[-1]

        return {
            "label": CORE_NODES["PORT"],
            "port_id": port_id,
            "name": record.get("portLabel")
        }

    @staticmethod
    def transform_product(record: Dict) -> Dict:

        product_uri = record.get("product", "")
        product_id = product_uri.split("/")[-1]

        return {
            "label": CORE_NODES["PRODUCT"],
            "product_id": product_id,
            "name": record.get("productLabel")
        }

    @staticmethod
    def transform_shipment(record: Dict) -> Dict:

        shipment_uri = record.get("shipment", "")
        shipment_id = shipment_uri.split("/")[-1]

        return {
            "label": CORE_NODES["SHIPMENT"],
            "shipment_id": shipment_id,
            "name": record.get("shipmentLabel")
        }

    @staticmethod
    def transform_risk(
        risk_id: str,
        risk_type: str,
        severity: float,
        description: str
    ) -> Dict:

        return {
            "label": CORE_NODES["RISK"],
            "risk_id": risk_id,
            "risk_type": risk_type,
            "severity": severity,
            "description": description
        }


    # RELATIONSHIP TRANSFORMATIONS
    @staticmethod
    def company_country_relationship(
        company_id: str,
        country_code: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COMPANY"],
            "source_id": company_id,

            "relationship":
                CORE_RELATIONSHIPS["LOCATED_IN"],

            "target_label": CORE_NODES["COUNTRY"],
            "target_id": country_code
        }

    @staticmethod
    def company_supplier_relationship(
        supplier_id: str,
        company_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COMPANY"],
            "source_id": supplier_id,

            "relationship":
                CORE_RELATIONSHIPS["SUPPLIES"],

            "target_label": CORE_NODES["COMPANY"],
            "target_id": company_id
        }

    @staticmethod
    def company_port_relationship(
        company_id: str,
        port_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COMPANY"],
            "source_id": company_id,

            "relationship":
                CORE_RELATIONSHIPS["USES_PORT"],

            "target_label": CORE_NODES["PORT"],
            "target_id": port_id
        }

    @staticmethod
    def company_risk_relationship(
        company_id: str,
        risk_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COMPANY"],
            "source_id": company_id,

            "relationship":
                CORE_RELATIONSHIPS["HAS_RISK"],

            "target_label": CORE_NODES["RISK"],
            "target_id": risk_id
        }

    @staticmethod
    def country_risk_relationship(
        country_code: str,
        risk_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COUNTRY"],
            "source_id": country_code,

            "relationship":
                CORE_RELATIONSHIPS["HAS_RISK"],

            "target_label": CORE_NODES["RISK"],
            "target_id": risk_id
        }

    @staticmethod
    def shipment_port_relationship(
        shipment_id: str,
        port_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["SHIPMENT"],
            "source_id": shipment_id,

            "relationship":
                CORE_RELATIONSHIPS["SHIPS_THROUGH"],

            "target_label": CORE_NODES["PORT"],
            "target_id": port_id
        }

    @staticmethod
    def dependency_relationship(
        company_id: str,
        dependency_company_id: str
    ) -> Dict:

        return {
            "source_label": CORE_NODES["COMPANY"],
            "source_id": company_id,

            "relationship":
                CORE_RELATIONSHIPS["DEPENDS_ON"],

            "target_label": CORE_NODES["COMPANY"],
            "target_id": dependency_company_id
        }


    # BULK TRANSFORMATIONS
    @staticmethod
    def transform_companies(
        records: List[Dict]
    ) -> List[Dict]:

        return [
            GraphTransformer.transform_company(record)
            for record in records
        ]

    @staticmethod
    def transform_countries(
        records: List[Dict]
    ) -> List[Dict]:

        return [
            GraphTransformer.transform_country(record)
            for record in records
        ]

    @staticmethod
    def transform_ports(
        records: List[Dict]
    ) -> List[Dict]:

        return [
            GraphTransformer.transform_port(record)
            for record in records
        ]

    @staticmethod
    def transform_products(
        records: List[Dict]
    ) -> List[Dict]:

        return [
            GraphTransformer.transform_product(record)
            for record in records
        ]

    @staticmethod
    def transform_shipments(
        records: List[Dict]
    ) -> List[Dict]:

        return [
            GraphTransformer.transform_shipment(record)
            for record in records
        ]