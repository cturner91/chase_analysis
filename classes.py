from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from bs4 import BeautifulSoup


class Personnel(Enum):
    CHASER = 'CHASER'
    PLAYER = 'PLAYER'
    TEAM = 'TEAM'


class ParserCommon:

    def _parse_date(text: str) -> datetime:
        return datetime.strptime(text, '%d/%m/%Y')

    def _parse_fc_result(text: str) -> tuple[str, int]:

        if 'Chaser' in text:
            final_chase_winner = Personnel.CHASER.value
            final_chase_margin_time = text[-5:]
            minutes, seconds = final_chase_margin_time.split(':')
            final_chase_margin = int(minutes) * 60 + int(seconds)
        elif 'Team' in text:
            final_chase_winner = Personnel.TEAM.value
            final_chase_margin = int(text.split(' ')[-1].strip())
        else:
            raise ValueError(f'Final chase result not recognised: {text}')

        return final_chase_winner, final_chase_margin

    def _parse_money(value: str) -> float:
        if 'no offer' in value:
            return None
        
        if 'p' in value:
            return int(value.replace('p', '')) / 100

        return float(value.replace('£', '').replace(',', ''))


@dataclass
class Episode(ParserCommon):
    series: int = None
    episode: int = None
    date: datetime = None
    team: str = None
    chaser: str = None
    players_in_final_chase: int = None
    prize_fund: float = None
    target: int = None
    winner: str = None
    winner_margin: int = None
    pushbacks_attempted: int = None
    pushbacks_completed: int = None
    chaser_accuracy: float = None
    chaser_speed: float = None
    final_chase_video: str = None
    
    def _parse_fc_target(text: str) -> tuple[int, int]:
        if '+' in text:
            base, pushbacks = [x.strip() for x in text.split('+')]
            return int(base), int(pushbacks)
        return int(text), 0
    
    @classmethod
    def from_html(cls, html: str) -> 'Episode':
        # the html should be the <tr>...</tr> contents
        soup = BeautifulSoup(html, features='html.parser')
        data = soup.find_all('td')

        winner, winner_margin = cls._parse_fc_result(data[7].text)
        target, extra_pushbacks = cls._parse_fc_target(data[6].text)

        series = int(data[1].text.split('.')[0].strip())
        episode = int(data[1].text.split('.')[1].strip().replace('*', ''))

        return Episode(
            date=cls._parse_date(data[0].text),
            series=series,
            episode=episode,
            team=data[2].text,
            chaser=data[3].text,
            players_in_final_chase=int(data[4].text),
            prize_fund=cls._parse_money(data[5].text),
            target=target,
            winner=winner,
            winner_margin=winner_margin,
            pushbacks_attempted=int(data[8].text),
            pushbacks_completed=int(data[9].text),
            chaser_accuracy=int(data[10].text[:-1]),
            chaser_speed=float(data[11].text),
            final_chase_video=data[12].text.strip(),
        )


@dataclass
class Player(ParserCommon):
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
            hth_winner = Personnel.PLAYER.value
        elif 'Caught' in text:
            hth_winner = Personnel.CHASER.value
        else:
            raise ValueError(f'HTH winner not recognised: {text}')
        hth_margin = int(text[-1])  # cannot be double digits

        return hth_winner, hth_margin
    
    def _parse_fc_correct(text: str) -> int:
        cleaned = text.split(' ')[0].strip()
        return int(cleaned) if cleaned else None

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
            cash_builder=cls._parse_money(data[3].text),
            chaser=data[4].text,
            lower_offer=cls._parse_money(data[5].text),
            higher_offer=cls._parse_money(data[6].text),
            chosen_offer=chosen_offer,
            hth_winner=hth_winner,
            hth_margin=hth_margin,
            final_chase_correct=final_chase_correct,
            final_chase_margin=final_chase_margin,
            final_chase_winner=final_chase_winner,
            amount_won=cls._parse_money(data[11].text),
        )
