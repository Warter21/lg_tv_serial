"""Tests for the LG TV coordinator."""

from unittest.mock import AsyncMock

import pytest

from custom_components.lg_tv_serial.coordinator import CoordinatorData, LgTvCoordinator


@pytest.mark.asyncio
async def test_media_state_is_only_polled_once_while_tv_stays_on():
    """Volume, mute and input queries must not repeatedly trigger the TV OSD."""
    api = AsyncMock()
    api.get_power_on.return_value = True

    coordinator = object.__new__(LgTvCoordinator)
    coordinator.api = api
    coordinator.data = CoordinatorData()
    coordinator._media_state_initialized = False

    await coordinator._async_update_data()
    await coordinator._async_update_data()

    api.get_power_on.assert_awaited_twice()
    api.get_mute.assert_awaited_once()
    api.get_volume.assert_awaited_once()
    api.get_input.assert_awaited_once()
    assert api.get_remote_control_lock.await_count == 2
    assert api.get_energy_saving.await_count == 2


@pytest.mark.asyncio
async def test_media_state_is_polled_again_after_power_cycle():
    """Media state is rediscovered when the TV comes back online."""
    api = AsyncMock()
    api.get_power_on.side_effect = [True, False, True]

    coordinator = object.__new__(LgTvCoordinator)
    coordinator.api = api
    coordinator.data = CoordinatorData()
    coordinator._media_state_initialized = False

    await coordinator._async_update_data()
    await coordinator._async_update_data()
    await coordinator._async_update_data()

    assert api.get_mute.await_count == 2
    assert api.get_volume.await_count == 2
    assert api.get_input.await_count == 2
