"""TCG card plaza component."""

from __future__ import annotations

import functools
import typing

from genshin import paginators, types
from genshin.client import cache, routes
from genshin.client.components import base
from genshin.models.genshin import card_plaza as models

__all__ = ["CardPlazaClient"]

DECK_PAGE_SIZE = 20
COMMENT_PAGE_SIZE = 20


class CardPlazaClient(base.BaseClient):
    """TCG card plaza component."""

    async def request_card_plaza(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        lang: typing.Optional[str] = None,
        params: typing.Optional[typing.Mapping[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ) -> typing.Mapping[str, typing.Any]:
        """Make a request towards the card plaza endpoint."""
        params = dict(params or {})
        params["lang"] = lang or self.lang

        url = routes.CARD_PLAZA_URL.get_url() / endpoint

        return await self.request(url, method=method, params=params, **kwargs)

    async def get_tcg_deck_labels(self, *, lang: typing.Optional[str] = None) -> typing.Sequence[models.TCGDeckLabel]:
        """Get card plaza labels, such as game modes and boss challenges."""
        data = await self.request_card_plaza(
            "labels",
            lang=lang,
            static_cache=cache.cache_key("card_plaza", endpoint="labels", lang=lang or self.lang),
        )

        return [models.TCGDeckLabel(**i) for i in data["tree"][0]["children"]]

    async def _get_tcg_character_cards(self, *, lang: typing.Optional[str] = None) -> list[models.TCGDeckCharacterCard]:
        data = await self.request_card_plaza(
            "roles",
            lang=lang,
            static_cache=cache.cache_key("card_plaza", endpoint="roles", lang=lang or self.lang),
        )

        return [models.TCGDeckCharacterCard(**i) for i in data["roles"]]

    async def _get_tcg_action_cards(
        self, character_ids: typing.Sequence[int], *, lang: typing.Optional[str] = None
    ) -> list[models.TCGDeckActionCard]:
        # talent cards are only returned for the characters passed in role_ids
        data = await self.request_card_plaza(
            "actions",
            method="POST",
            lang=lang,
            data=dict(role_ids=character_ids),
            static_cache=cache.cache_key("card_plaza", endpoint="actions", lang=lang or self.lang),
        )

        return [models.TCGDeckActionCard(**i) for i in data["actions"]]

    async def get_tcg_cards(
        self,
        card_types: typing.Optional[typing.Sequence[models.TCGDeckCardType]] = None,
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Sequence[typing.Union[models.TCGDeckCharacterCard, models.TCGDeckActionCard]]:
        """Get TCG cards available in the card plaza.

        Args:
            card_types: Types of cards to get, defaults to all cards.
            lang: Language of the response.

        Returns:
            Character cards and/or action cards, depending on ``card_types``.
        """
        wanted = set(card_types or models.TCGDeckCardType)

        # character IDs are always needed since action cards only include talents of the requested characters
        character_cards = await self._get_tcg_character_cards(lang=lang)
        cards: list[typing.Union[models.TCGDeckCharacterCard, models.TCGDeckActionCard]] = []

        if models.TCGDeckCardType.CHARACTER in wanted:
            cards.extend(character_cards)

        if wanted - {models.TCGDeckCardType.CHARACTER}:
            action_cards = await self._get_tcg_action_cards([card.id for card in character_cards], lang=lang)
            cards.extend(card for card in action_cards if card.type in wanted)

        return cards

    @typing.overload
    async def get_tcg_card_effect(
        self, card: models.TCGDeckCharacterCard, *, lang: typing.Optional[str] = ...
    ) -> typing.Sequence[models.TCGDeckSkill]: ...
    @typing.overload
    async def get_tcg_card_effect(
        self, card: models.TCGDeckActionCard, *, lang: typing.Optional[str] = ...
    ) -> models.TCGDeckActionCardEffect: ...
    @typing.overload
    async def get_tcg_card_effect(
        self, card: int, *, lang: typing.Optional[str] = ...
    ) -> typing.Union[typing.Sequence[models.TCGDeckSkill], models.TCGDeckActionCardEffect]: ...
    async def get_tcg_card_effect(
        self,
        card: typing.Union[int, models.TCGDeckCharacterCard, models.TCGDeckActionCard],
        *,
        lang: typing.Optional[str] = None,
    ) -> typing.Union[typing.Sequence[models.TCGDeckSkill], models.TCGDeckActionCardEffect]:
        """Get the effect of a TCG card.

        Args:
            card: Card or card ID. Bare IDs below 10000 are treated as character cards.
            lang: Language of the response.

        Returns:
            Skills of a character card, or the effect description and cost of an action card.
        """
        card_id = card if isinstance(card, int) else card.id
        is_character = isinstance(card, models.TCGDeckCharacterCard) or (isinstance(card, int) and card_id < 10000)

        if is_character:
            data = await self.request_card_plaza(
                "role/skill",
                lang=lang,
                params=dict(id=card_id),
                static_cache=cache.cache_key("card_plaza", endpoint="skill", id=card_id, lang=lang or self.lang),
            )
            return [models.TCGDeckSkill(**i) for i in data["skills"]]

        data = await self.request_card_plaza(
            "action/skill",
            lang=lang,
            params=dict(id=card_id),
            static_cache=cache.cache_key("card_plaza", endpoint="action_skill", id=card_id, lang=lang or self.lang),
        )
        return models.TCGDeckActionCardEffect(**data)

    async def _get_tcg_deck_page(
        self,
        token: str,
        *,
        page_size: int,
        label_id: int,
        character_ids: typing.Sequence[int],
        keywords: str,
        order: str,
        lang: typing.Optional[str] = None,
    ) -> tuple[str, typing.Sequence[models.TCGDeck]]:
        """Get a single page of card plaza decks."""
        body: dict[str, typing.Any] = dict(
            keywords=keywords,
            label_id=label_id,
            order=order,
            role_card_id=character_ids,
            next_page_token=token,
            page_size=page_size,
        )

        data = await self.request_card_plaza("index", method="POST", lang=lang, data=body)

        return data["next_page_token"], [models.TCGDeck(**i) for i in data["list"]]

    def get_tcg_decks(
        self,
        label: typing.Optional[types.IDOr[models.TCGDeckLabel]] = None,
        *,
        characters: typing.Optional[typing.Sequence[types.IDOr[models.TCGDeckCharacterCard]]] = None,
        keywords: str = "",
        newest: bool = False,
        limit: typing.Optional[int] = None,
        page_size: int = DECK_PAGE_SIZE,
        lang: typing.Optional[str] = None,
    ) -> paginators.TokenPaginator[models.TCGDeck]:
        """Get decks from the card plaza.

        Args:
            label: Label to filter by, defaults to "General".
            characters: Character cards the decks must contain.
            keywords: Keywords to search for.
            newest: Sort by newest instead of most popular.
            limit: Maximum amount of decks to return.
            page_size: Amount of decks to fetch per request.
            lang: Language of the response.

        Returns:
            Paginator over the matching decks.
        """
        return paginators.TokenPaginator(
            functools.partial(
                self._get_tcg_deck_page,
                page_size=page_size,
                label_id=int(label) if label is not None else 1,
                character_ids=[int(i) for i in characters or []],
                keywords=keywords,
                order="O_LATEST" if newest else "O_HOT",
                lang=lang,
            ),
            limit=limit,
            page_size=page_size,
        )

    async def get_tcg_deck(
        self,
        deck: typing.Union[str, models.TCGDeck],
        *,
        lang: typing.Optional[str] = None,
    ) -> models.TCGDeck:
        """Get a card plaza deck by its ID."""
        deck_id = deck if isinstance(deck, str) else deck.id

        data = await self.request_card_plaza(
            "detail",
            lang=lang,
            params=dict(id=deck_id),
            cache=cache.cache_key("card_plaza", endpoint="detail", id=deck_id, lang=lang or self.lang),
        )

        return models.TCGDeck(**data["detail"])

    async def _get_tcg_deck_comment_page(
        self, token: str, *, deck_id: str
    ) -> tuple[str, typing.Sequence[models.TCGDeckComment]]:
        """Get a single page of comments on a card plaza deck."""
        params = dict(app_id=10034, game_biz="hk4e", entity_key=deck_id, next=token or 0, mode=3)

        url = routes.BOULEUTERION_URL.get_url() / "account/reply/list"
        data = await self.request(url, params=params)

        return str(data["cursor"]["next"]), [models.TCGDeckComment(**i) for i in data["list"]]

    def get_tcg_deck_comments(
        self,
        deck: typing.Union[str, models.TCGDeck],
        *,
        limit: typing.Optional[int] = None,
    ) -> paginators.TokenPaginator[models.TCGDeckComment]:
        """Get comments on a card plaza deck."""
        deck_id = deck if isinstance(deck, str) else deck.id

        return paginators.TokenPaginator(
            functools.partial(self._get_tcg_deck_comment_page, deck_id=deck_id),
            limit=limit,
            page_size=COMMENT_PAGE_SIZE,
        )
