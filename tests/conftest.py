"""Shared test configuration."""

import os

from hypothesis import HealthCheck, settings

# CI runs more examples than a local run; select with HYPOTHESIS_PROFILE=ci.
settings.register_profile("dev", max_examples=100)
settings.register_profile(
    "ci", max_examples=500, deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))
