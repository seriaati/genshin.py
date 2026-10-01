import genshin


async def test_tcg_deck_labels(client: genshin.Client):
    data = await client.get_tcg_deck_labels()

    assert data


async def test_tcg_cards(client: genshin.Client):
    data = await client.get_tcg_cards()

    assert data


async def test_tcg_character_cards(client: genshin.Client):
    data = await client.get_tcg_cards([genshin.models.TCGDeckCardType.CHARACTER])

    assert all(isinstance(card, genshin.models.TCGDeckCharacterCard) for card in data)


async def test_tcg_character_card_effect(client: genshin.Client):
    data = await client.get_tcg_card_effect(2301)

    assert data


async def test_tcg_action_card_effect(client: genshin.Client):
    data = await client.get_tcg_card_effect(312004)

    assert isinstance(data, genshin.models.TCGDeckActionCardEffect)


async def test_tcg_decks(client: genshin.Client):
    data = await client.get_tcg_decks(characters=[1105, 1106], limit=10, page_size=10)

    assert data


async def test_tcg_deck(client: genshin.Client):
    data = await client.get_tcg_deck("6473d2579af0ae7be3f22bba")

    assert data


async def test_tcg_deck_comments(client: genshin.Client):
    data = await client.get_tcg_deck_comments("6473d2579af0ae7be3f22bba", limit=10)

    assert data
