from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from bs4 import BeautifulSoup


class Personnel(StrEnum):
    CHASER = 'CHASER'
    PLAYER = 'PLAYER'
    TEAM = 'TEAM'


def _clean_money(value: str) -> float:
    if 'no offer' in value:
        return None
    
    if 'p' in value:
        return int(value.replace('p', '')) / 100

    return float(value.replace('£', '').replace(',', ''))


@dataclass
class Episode:
    series: int
    episode: int
    date: datetime
    team: str
    chaser: str
    players_in_final_chase: int
    prize_fund: float
    target: int
    winner: str
    winner_margin: int
    pushbacks_attempted: int
    pushbacks_completed: int
    chaser_accuracy: float
    chaser_speed: float
    final_chase_video: str

    def from_html(html: str) -> 'Episode':
        pass


@dataclass
class Player:
    series: int = None
    episode: int = None
    date: datetime = None
    player_number: int = None
    name: str  = None
    cash_builder: int = None
    chaser: str = None
    lower_offer: float = None
    higher_offer: float = None
    chosen_offer: int = None  # -1, 0, 1
    hth_winner: str = None  # chaser / player
    hth_margin: int = None
    final_chase_correct: int = None
    final_chase_winner: str = None  # chaser / team
    final_chase_margin: int = None
    amount_won: float = None

    def _parse_date(text: str) -> datetime:
        return datetime.strptime(text, '%d/%m/%Y')
    
    def _parse_chosen_offer(text: str) -> int:
        if '/\\' in text:
            return 1
        elif '\\/' in text:
            return -1
        elif '=' in text:
            return 0
        else:
            raise ValueError(f'Chosen offer not recognised: {text}')

    def _parse_hth(text: str) -> tuple[str, int]:
        if 'Home' in text:
            hth_winner = Personnel.PLAYER
        elif 'Caught' in text:
            hth_winner = Personnel.CHASER
        else:
            raise ValueError(f'HTH winner not recognised: {text}')
        hth_margin = int(text[-1])  # cannot be double digits

        return hth_winner, hth_margin
    
    def _parse_fc_correct(text: str) -> int:
        cleaned = text.split(' ')[0].strip()
        return int(cleaned) if cleaned else None
    
    def _parse_fc_result(text: str) -> tuple[str, int]:

        if 'Chaser' in text:
            final_chase_winner = Personnel.CHASER
            final_chase_margin_time = text[-5:]
            minutes, seconds = final_chase_margin_time.split(':')
            final_chase_margin = int(minutes) * 60 + int(seconds)
        elif 'Team' in text:
            final_chase_winner = Personnel.TEAM
            final_chase_margin = int(text.split(' ')[-1].strip())
        else:
            raise ValueError(f'Final chase result not recognised: {text}')

        return final_chase_winner, final_chase_margin

    @classmethod
    def from_html(cls, html: str) -> 'Player':
        # the html should be the <tr>...</tr> contents
        soup = BeautifulSoup(html, features='html.parser')
        data = soup.find_all('td')

        # if len(data) != 12:
        #     raise ValueError('Player data row must have 12 columns')

        dt = cls._parse_date(data[0].text)
        chosen_offer = cls._parse_chosen_offer(data[7].text)
        hth_winner, hth_margin = cls._parse_hth(data[8].text)
        final_chase_correct = cls._parse_fc_correct(data[9].text)
        final_chase_winner, final_chase_margin = cls._parse_fc_result(data[10].text)

        return Player(
            date=dt,
            player_number=int(data[1].text.replace('P', '')),
            name=data[2].text,
            cash_builder=_clean_money(data[3].text),
            chaser=data[4].text,
            lower_offer=_clean_money(data[5].text),
            higher_offer=_clean_money(data[6].text),
            chosen_offer=chosen_offer,
            hth_winner=hth_winner,
            hth_margin=hth_margin,
            final_chase_correct=final_chase_correct,
            final_chase_margin=final_chase_margin,
            final_chase_winner=final_chase_winner,
            amount_won=_clean_money(data[11].text),
        )
