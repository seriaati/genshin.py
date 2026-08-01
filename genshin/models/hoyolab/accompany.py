from typing import Any, Mapping, Optional, Sequence

from pydantic import field_validator

from genshin import types
from genshin.models.model import Aliased, APIModel, UnixDateTime

__all__ = (
    "AccompanyAction",
    "AccompanyAvatarFrame",
    "AccompanyAvatarFrameConfig",
    "AccompanyAwardInfo",
    "AccompanyCharacter",
    "AccompanyCharacterAttribute",
    "AccompanyCharacterDetails",
    "AccompanyCharacterGame",
    "AccompanyCharacterInfo",
    "AccompanyCharacterProfile",
    "AccompanyFeedInfo",
    "AccompanyInfo",
    "AccompanyJump",
    "AccompanyLanternBonus",
    "AccompanyLanternConfig",
    "AccompanyLanternSign",
    "AccompanyLanternTemplate",
    "AccompanyMomentPost",
    "AccompanyPendant",
    "AccompanyPopupDoc",
    "AccompanyRecentPoster",
    "AccompanyResult",
    "AccompanyTitle",
    "AccompanyTopicStats",
    "AccompanyVoiceLine",
    "AccompanyVoiceSetting",
    "AccompanyWidget",
    "AccompanyWidgetImage",
    "AccompanyWikiImage",
    "AccompanyWikiVideo",
)


class AccompanyCharacterInfo(APIModel):
    """Accompany character info."""

    role_id: int
    game_id: int
    name: str
    brief_name: str
    topic_id: int
    game_name: str


class AccompanyCharacterProfile(APIModel):
    """Accompany character color and images."""

    card_color: str
    bg_dark_color: str
    bg_light_color: str
    bg_card_color: str

    card_image: str = Aliased("card_img_url")
    video: str = Aliased("full_screen_video_265")
    icon: str = Aliased("icon_url")


class AccompanyCharacter(APIModel):
    """Accompany character."""

    info: AccompanyCharacterInfo = Aliased("basic")
    profile: AccompanyCharacterProfile = Aliased("attr_profile")
    attribute_ids: Sequence[int]


class AccompanyCharacterAttribute(APIModel):
    """Accompany character attribute."""

    id: int
    icon: str = Aliased("icon_url")
    corner_icon: str = Aliased("corner_icon_url")


class AccompanyCharacterGame(APIModel):
    """Accompany character game."""

    attributes: Sequence[Sequence[AccompanyCharacterAttribute]] = Aliased("attribute_group_list")
    id: int = Aliased("game_id")
    icon: str = Aliased("game_icon")
    characters: Sequence[AccompanyCharacter] = Aliased("role_list")

    @field_validator("attributes", mode="before")
    def __unnest_attributes(cls, v: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        return [group["attribute_list"] for group in v]

    @property
    def game(self) -> types.Game:
        if self.id == 2:
            return types.Game.GENSHIN
        if self.id == 6:
            return types.Game.STARRAIL
        if self.id == 8:
            return types.Game.ZZZ

        raise ValueError(f"Unknown game ID: {self.id}")


class AccompanyResult(APIModel):
    """Accompany result."""

    accompany_days: int
    points_increased: int = Aliased("increase_accompany_point")


class AccompanyInfo(APIModel):
    """Accompany progress of a character."""

    days: int = Aliased("accompany_days")
    quarter_days: int = Aliased("accompany_quarter_days")
    accompanied_today: bool = Aliased("is_accompany_today")
    can_accompany: bool
    points: int = Aliased("accompany_point")
    available_points: int = Aliased("available_accompany_point")


class AccompanyVoiceLine(APIModel):
    """Accompany character voice line."""

    voice_url: str = Aliased("voice")
    text: str = Aliased("script")


class AccompanyWikiVideo(APIModel):
    """Accompany character wiki video."""

    video_id: str
    video_url: str
    cover_url: str
    synced_at: UnixDateTime = Aliased("sync_unix")
    sort: int


class AccompanyWikiImage(APIModel):
    """Accompany character wiki gallery image."""

    image_url: str
    origin_url: str
    height: int
    width: int
    size: int
    synced_at: UnixDateTime = Aliased("sync_unix")


class AccompanyJump(APIModel):
    """Deep link to a location in the app or on the web."""

    text: str
    app_path: str
    web_path: str


class AccompanyFeedInfo(APIModel):
    """Post counts of an accompany character's feed."""

    fan_art_posts: int = Aliased("fan_art_post_num")
    discussion_posts: int = Aliased("discussion_post_num")
    yesterday_posts: int = Aliased("yesterday_post_num")
    total_posts: int = Aliased("total_post_num")


class AccompanyWidgetImage(APIModel):
    """Widget image asset in two resolutions."""

    img_2x: str
    img_3x: str


class AccompanyWidget(APIModel):
    """Accompany character widget image assets."""

    role_image: AccompanyWidgetImage
    component_image: AccompanyWidgetImage = Aliased("role_component_image")
    emoji_image: AccompanyWidgetImage = Aliased("emo_url")
    background_url: str = Aliased("bg_url")


class AccompanyMomentPost(APIModel):
    """Official post shown on an accompany character's page."""

    id: int = Aliased("post_id")
    game_id: int
    subject: str
    content: str
    lang: str
    created_at: UnixDateTime


class AccompanyPendant(APIModel):
    """Cosmetic unlockable with accompany points."""

    id: int = Aliased("pendant_id")
    icon: str = Aliased("icon_url")
    lifetime: str
    source: str
    type: str = Aliased("pendant_type")
    cost: int = Aliased("point")
    award_type: str
    is_owned: bool
    can_use: bool
    in_use: bool
    jump: Optional[AccompanyJump] = Aliased("use_jump", default=None)


class AccompanyAction(APIModel):
    """Action that grants accompany points."""

    action: str
    points: int = Aliased("point")
    max_points_per_day: int = Aliased("max_point_per_day")
    done: bool
    jump: Optional[AccompanyJump] = None


class AccompanyTitle(APIModel):
    """Title earnable through accompanying."""

    title: str
    name: str = Aliased("title_name")
    description: str = Aliased("title_desc")
    icon: str = Aliased("icon_url")
    highlight_icon: str = Aliased("highlight_icon_url")
    is_owned: bool


class AccompanyAwardInfo(APIModel):
    """Accompany rewards and point-earning actions."""

    pendants: Sequence[AccompanyPendant] = Aliased("pendant_list")
    actions: Sequence[AccompanyAction] = Aliased("action_list")
    titles: Sequence[AccompanyTitle] = Aliased("title_list")


class AccompanyLanternBonus(APIModel):
    """Lantern sign reward tier."""

    required_points: int = Aliased("require_accompany_points")
    pendant_id: int
    lifetime: int
    title: str
    light_icon: str = Aliased("light_icon_url")
    dark_icon: str = Aliased("dark_icon_url")
    description: str = Aliased("desc")


class AccompanyLanternTemplate(APIModel):
    """Suggested post template for the lantern sign event."""

    subject: str
    game_id: int
    classification_id: int
    topic_ids: Sequence[int]


class AccompanyLanternConfig(APIModel):
    """Lantern sign event configuration."""

    bonuses: Sequence[AccompanyLanternBonus]
    templates: Sequence[AccompanyLanternTemplate] = Aliased("lantern_sign_templates")
    jump: AccompanyJump = Aliased("pop_up_jump")
    quarter_begin_at: int
    quarter_end_at: int
    quarter_left_seconds: int
    light_icon: str = Aliased("light_icon_url")
    dark_icon: str = Aliased("dark_icon_url")


class AccompanyLanternSign(APIModel):
    """Lantern sign event progress."""

    config: AccompanyLanternConfig = Aliased("lantern_sign_conf")
    pendant_id: int = Aliased("lantern_pendant_id")
    post_points: int
    total_post_points: int
    post_points_today: int
    accompany_points: int
    total_accompany_points: int
    accompany_days: int
    accompanied_today: bool = Aliased("is_accompany_today")
    wearing: bool
    has_got: bool
    expire_at: int


class AccompanyPopupDoc(APIModel):
    """Avatar frame popup document."""

    day: str = Aliased("the_day")
    icon: str
    description: str = Aliased("desc")


class AccompanyAvatarFrameConfig(APIModel):
    """Avatar frame reward configuration."""

    icon: str = Aliased("icon_url")
    popup_docs: Sequence[AccompanyPopupDoc] = Aliased("pop_up_doc")
    jump: AccompanyJump = Aliased("pop_up_jump")
    quarter_begin_at: int
    quarter_end_at: int
    quarter_left_seconds: int


class AccompanyAvatarFrame(APIModel):
    """Quarterly avatar frame reward progress."""

    config: AccompanyAvatarFrameConfig = Aliased("avatar_frame_conf")
    id: int = Aliased("avatar_frame_id")
    quarter_days: int = Aliased("accompany_quarter_days")
    accompanied_today: bool = Aliased("is_accompany_today")


class AccompanyRecentPoster(APIModel):
    """Recent poster in an accompany character's topic."""

    uid: int
    posted_at: UnixDateTime = Aliased("post_time")


class AccompanyTopicStats(APIModel):
    """Community statistics of an accompany character's topic."""

    topic_id: int
    views: int = Aliased("view_num")
    replies: int = Aliased("reply_num")
    members: int = Aliased("member_num")
    posts: int = Aliased("post_num")
    today_posts: int = Aliased("today_increase_post_num")
    week_posts: int = Aliased("seven_days_increase_post_num")
    recent_posters: Sequence[AccompanyRecentPoster] = Aliased("recent_post_user_info_list")


class AccompanyCharacterDetails(APIModel):
    """Accompany character page details."""

    info: AccompanyCharacterInfo = Aliased("basic")
    profile: AccompanyCharacterProfile = Aliased("attr_profile")
    accompany_info: AccompanyInfo
    voice_scripts: Mapping[str, Sequence[AccompanyVoiceLine]] = Aliased("attr_wiki_voice_script")
    videos: Sequence[AccompanyWikiVideo] = Aliased("attr_wiki_video")
    gallery: Sequence[AccompanyWikiImage] = Aliased("attr_wiki_gallery")
    widget: Optional[AccompanyWidget] = Aliased("attr_widget", default=None)
    moment_posts: Sequence[AccompanyMomentPost] = Aliased("attr_moment")
    feed_info: AccompanyFeedInfo
    game_jump_url: str
    award_info: Optional[AccompanyAwardInfo] = None
    lantern_sign: Optional[AccompanyLanternSign] = None
    avatar_frame: Optional[AccompanyAvatarFrame] = None
    stats: Optional[AccompanyTopicStats] = None
    """Topic statistics, not part of role_info but passed in by the client."""

    @field_validator("voice_scripts", mode="before")
    def __unnest_voice_scripts(cls, v: Optional[dict[str, Any]]) -> dict[str, Any]:
        return {name: script["list"] for name, script in v["scripts"].items()} if v else {}

    @field_validator("videos", mode="before")
    def __unnest_videos(cls, v: Optional[dict[str, Any]]) -> list[Any]:
        return v["videos"] if v else []

    @field_validator("gallery", mode="before")
    def __unnest_gallery(cls, v: Optional[dict[str, Any]]) -> list[Any]:
        return v["images"] if v else []

    @field_validator("moment_posts", mode="before")
    def __unnest_moment_posts(cls, v: Optional[dict[str, Any]]) -> list[Any]:
        return [post["post"] for post in v["post_list"]] if v else []


class AccompanyVoiceSetting(APIModel):
    """Voice and subtitle language setting of an accompany character."""

    voice_lang: str
    script_lang: str
    updated_at: UnixDateTime = Aliased("setting_unix")
