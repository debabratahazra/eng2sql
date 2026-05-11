# US-027: MongoDBConnector Service

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 5
**Priority**: Must Have

## User Story

> As a **developer**, I want a `MongoDBConnector` service class that encapsulates all
> pymongo connection logic so that the sidebar component can connect to a MongoDB
> server, list databases, and retrieve a database object without handling driver
> details directly.

## Acceptance Criteria

```gherkin
Feature: MongoDBConnector Service

  Scenario: connect() returns a MongoClient on valid credentials
    Given a valid MongoConfig with host, port, username, and password
    When MongoDBConnector.connect(config) is called
    Then a connected MongoClient is returned
    And the connection is verified with a ping command

  Scenario: connect() raises DatabaseConnectionError on failure
    Given an unreachable host or invalid credentials in MongoConfig
    When MongoDBConnector.connect(config) is called
    Then a DatabaseConnectionError is raised
    And the original exception is attached as __cause__

  Scenario: connect() with no-auth config succeeds without credentials
    Given a MongoConfig with auth_mechanism "None / No Auth"
    When MongoDBConnector.connect(config) is called
    Then the MongoClient is created without auth parameters

  Scenario: list_databases() returns filtered list
    Given a connected MongoClient with databases admin, local, config, mydb
    When MongoDBConnector.list_databases(client) is called
    Then ["mydb"] is returned (system databases excluded)

  Scenario: get_database() returns correct Database object
    Given a connected MongoClient
    When MongoDBConnector.get_database(client, "mydb") is called
    Then a pymongo Database object for "mydb" is returned
```

## Technical Notes
- New file: `src/services/mongo_connector.py`
- `MongoConfig` dataclass in `src/models/config.py` with fields: `host`, `port`,
  `username`, `password`, `auth_source` (default `"admin"`),
  `auth_mechanism` (default `"SCRAM-SHA-256"`), `connect_timeout_ms` (default `5000`)
- `connection_uri` property: builds `mongodb://user:pass@host:port/` with
  `urllib.parse.quote_plus` encoding for password
- Ping via `client.admin.command("ping")` to verify connectivity
- Import guard: `from pymongo import MongoClient`; raise `ImportError` message if not installed
- System databases constant: `frozenset({"admin", "local", "config"})`

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
