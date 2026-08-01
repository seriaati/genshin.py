import pytest

import genshin


async def test_notes(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_notes()
    assert data


async def test_diary(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_diary()
    assert data


async def test_user(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_user()
    assert data


async def test_agents(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_agents()
    assert data


async def test_bangboos(zzz_client: genshin.Client):
    data = await zzz_client.get_bangboos()
    assert data


async def test_zzz_agent_info(zzz_client: genshin.Client):
    data = await zzz_client.get_zzz_agent_info(1011)
    assert data


async def test_zzz_upgrade_guide_agents(zzz_client: genshin.Client):
    agents = await zzz_client.get_zzz_upgrade_guide_agents()
    assert agents


async def test_zzz_agent_upgrade_guide(zzz_client: genshin.Client):
    agents = await zzz_client.get_zzz_upgrade_guide_agents()
    unlocked = [agent for agent in agents if agent.unlocked]
    assert unlocked, "Account has no unlocked agents to test with."

    guides = await zzz_client.get_zzz_agent_upgrade_guide(unlocked[0].id)
    assert guides
    assert guides[0].avatar.id == unlocked[0].id


async def test_zzz_agent_upgrade_guide_batch_limit(zzz_client: genshin.Client):
    with pytest.raises(ValueError, match="more than 10"):
        await zzz_client.get_zzz_agent_upgrade_guide(list(range(11)))


async def test_all_zzz_agent_upgrade_guides(zzz_client: genshin.Client):
    guides = await zzz_client.get_all_zzz_agent_upgrade_guides()
    assert guides


async def test_all_zzz_agent_upgrade_guides_including_locked(zzz_client: genshin.Client):
    unlocked = await zzz_client.get_all_zzz_agent_upgrade_guides()
    everything = await zzz_client.get_all_zzz_agent_upgrade_guides(unlocked_only=False)
    assert len(everything) >= len(unlocked)


async def test_shiyu_defense(zzz_client: genshin.Client):
    data = await zzz_client.get_shiyu_defense()
    assert data


async def test_deadly_assault(zzz_client: genshin.Client):
    data = await zzz_client.get_deadly_assault()
    assert data


async def test_lost_void_summary(zzz_client: genshin.Client):
    data = await zzz_client.get_lost_void_summary()
    assert data


async def test_threshold_simulation_brief(zzz_client: genshin.Client):
    brief = await zzz_client.get_threshold_simulation_brief()
    assert brief


async def test_threshold_simulation(zzz_client: genshin.Client):
    data = await zzz_client.get_threshold_simulation()
    assert data


async def test_threshold_simulation_by_uid(zzz_client: genshin.Client, zzz_uid: int):
    data_by_uid = await zzz_client.get_threshold_simulation(uid=zzz_uid)
    assert data_by_uid


async def test_zzz_event_calendar(zzz_client: genshin.Client):
    calendar = await zzz_client.get_zzz_event_calendar()
    assert calendar


async def test_zzz_gacha_calendar(zzz_client: genshin.Client):
    calendar = await zzz_client.get_zzz_gacha_calendar()
    assert calendar


async def test_zzz_gacha_info(zzz_client: genshin.Client):
    gacha_info = await zzz_client.get_zzz_gacha_info()
    assert gacha_info
