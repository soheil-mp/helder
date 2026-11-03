# ADR-0020: Privacy, attribution and source terms by construction

- **Status:** Accepted
- **Date:** 2026-11-03

## Context

Helder combines public environmental data from several organisations with different terms.
Some metadata names organisations; none should contain people. Re-publishing data requires
attribution, and one candidate source (zwemwater.nl) limits reuse to reporting during the
bathing season.

## Decision

- **No personal data.** Connectors keep fields through allowlists, not deny-lists; a test fails
  if an unexpected field reaches the `raw` layer. Organisation identifiers (such as a BRO data
  owner's Chamber of Commerce number) are kept only for attribution. No user accounts, no
  analytics cookies, no contact details for alerts.
- **Client identification without personal data:** the optional RWS `X-API-KEY` header carries
  a project identifier from configuration, never an e-mail address.
- **Attribution:** a source registry (`reference/sources.yaml`) holds each source's name,
  licence or terms, required citation and retrieval rules. Every API response, export, snapshot
  and dashboard view carries the sources and retrieval times of the data it shows.
- **Terms first:** a connector cannot be enabled until its source entry records the licence
  text and a reviewer confirms it. zwemwater.nl is excluded; Helder links to it for official
  bathing advice.
- **No advice:** Helder is informational and links to the responsible authorities.

## Consequences

- Attribution is automatic and complete.
- Some convenient sources stay out until their terms are clear.
