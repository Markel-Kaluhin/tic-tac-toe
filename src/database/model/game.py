from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .base import Base

metadata = Base.metadata  # type: ignore [attr-defined] # pylint: disable=no-member


class GameResult(Base):
    __tablename__ = "game_result"

    id = Column(Integer, primary_key=True)
    game_id = Column(ForeignKey("game.id"))
    user_id = Column(ForeignKey("user.id"))
    is_winner = Column(Boolean)
    symbol = Column(String(1))


class GameUserDecision(Base):
    __tablename__ = "game_user_decision"

    id = Column(Integer, primary_key=True)
    game_id = Column(ForeignKey("game.id"))
    user_id = Column(ForeignKey("user.id"))
    coordinate_x = Column(Integer)
    coordinate_y = Column(Integer)


class LeagueSeason(Base):
    __tablename__ = "league_season"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)


class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    league_season_id = Column(ForeignKey("league_season.id"))
