"""
BusinessLens AI — Connector Factory

Creates the correct connector given a DBConnection record.
SSRF guard must be applied BEFORE calling this factory (done in ConnectionService).
"""

from __future__ import annotations

from app.connectors.base_connector import BaseDBConnector
from app.core.exceptions import ConnectorNotSupportedError
from app.core.security import decrypt_credential
from app.models.connection import ConnectionType, SUPPORTED_CONNECTOR_TYPES, PLANNED_CONNECTOR_TYPES


class ConnectorFactory:
    """
    Creates connector instances from decrypted connection parameters.
    All credential decryption happens here — connectors receive plaintext.
    """

    def create_from_model(self, connection) -> BaseDBConnector:
        """
        Create a connector from a DBConnection ORM model.
        Decrypts the password before passing to the connector.
        """
        ct = connection.connection_type

        if ct not in SUPPORTED_CONNECTOR_TYPES and ct not in PLANNED_CONNECTOR_TYPES:
            raise ConnectorNotSupportedError(db_type=ct, planned=False)

        if ct in PLANNED_CONNECTOR_TYPES:
            raise ConnectorNotSupportedError(db_type=ct, planned=True)

        if ct == ConnectionType.POSTGRESQL:
            from app.connectors.postgresql_connector import PostgreSQLConnector
            password = ""
            if connection.encrypted_password:
                password = decrypt_credential(connection.encrypted_password)
            return PostgreSQLConnector(
                host=connection.host,
                port=connection.port or 5432,
                database=connection.database,
                username=connection.username,
                password=password,
                ssl=connection.ssl_enabled,
            )

        if ct in (ConnectionType.CSV, ConnectionType.EXCEL):
            from app.connectors.file_connector import FileConnector
            return FileConnector(
                file_path=connection.file_path,
                connection_type=ct,
            )

        raise ConnectorNotSupportedError(db_type=ct, planned=False)

    def create_from_params(
        self,
        connection_type: str,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        username: str | None = None,
        password: str | None = None,   # plaintext (for connection test only)
        ssl: bool = False,
        file_path: str | None = None,
    ) -> BaseDBConnector:
        """
        Create a connector directly from parameters.
        Used for connection testing BEFORE saving the connection.
        password is passed as plaintext here (not yet encrypted).
        """
        if connection_type == ConnectionType.POSTGRESQL:
            from app.connectors.postgresql_connector import PostgreSQLConnector
            return PostgreSQLConnector(
                host=host or "localhost",
                port=port or 5432,
                database=database or "",
                username=username or "",
                password=password or "",
                ssl=ssl,
            )

        if connection_type in (ConnectionType.CSV, ConnectionType.EXCEL):
            from app.connectors.file_connector import FileConnector
            return FileConnector(file_path=file_path or "", connection_type=connection_type)

        if connection_type in PLANNED_CONNECTOR_TYPES:
            raise ConnectorNotSupportedError(db_type=connection_type, planned=True)

        raise ConnectorNotSupportedError(db_type=connection_type, planned=False)
