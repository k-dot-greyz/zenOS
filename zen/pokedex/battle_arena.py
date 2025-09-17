"""
zenOS Battle Arena - Model vs Model Combat System
Where AI models duke it out based on their stats!
"""

import random
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class BattleMove(Enum):
    """Types of moves models can perform"""
    ANALYZE = "analyze"  # Uses intelligence
    CREATE = "create"    # Uses creativity
    SPEED_BLITZ = "speed_blitz"  # Uses speed
    DEFEND = "defend"    # Uses defense
    SPECIAL = "special"  # Uses special abilities
    COST_DRAIN = "cost_drain"  # Uses cost efficiency

@dataclass
class Fighter:
    """A model ready for battle"""
    id: str
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    special: int
    cost: int
    abilities: List[str]
    rarity: str
    
    @property
    def is_alive(self) -> bool:
        return self.hp > 0
    
    @property
    def hp_percentage(self) -> float:
        return (self.hp / self.max_hp) * 100
    
    def take_damage(self, damage: int) -> int:
        """Take damage, return actual damage dealt"""
        actual_damage = max(0, damage - (self.defense // 4))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal HP, return actual amount healed"""
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal

class BattleArena:
    """The arena where model battles take place"""
    
    def __init__(self, pokedex_path: Path = Path("pokedex")):
        self.pokedex_path = pokedex_path
        self.models = self._load_models()
        self.battle_log: List[str] = []
        self.turn_count = 0
        
    def _load_models(self) -> Dict[str, Dict]:
        """Load models from Pokédex"""
        models_file = self.pokedex_path / "models.yaml"
        if models_file.exists():
            with open(models_file) as f:
                data = yaml.safe_load(f)
                return {m['id']: m for m in data.get('models', [])}
        return {}
    
    def create_fighter(self, model_id: str) -> Optional[Fighter]:
        """Create a fighter from a model ID"""
        if model_id not in self.models:
            return None
            
        model = self.models[model_id]
        combat_stats = model.get('combat_stats', {})
        
        # If no combat stats, calculate basic ones
        if not combat_stats:
            stats = model.get('stats', {})
            combat_stats = {
                'hp': 100,
                'attack': stats.get('intelligence', 70),
                'defense': stats.get('reliability', 70),
                'speed': stats.get('speed', 70),
                'special': len(model.get('abilities', [])) * 10,
                'cost': 100 - min(model.get('cost_per_1k', {}).get('input', 0.001) * 100, 95)
            }
        
        return Fighter(
            id=model_id,
            name=model.get('name', model_id),
            hp=combat_stats.get('hp', 100),
            max_hp=combat_stats.get('hp', 100),
            attack=combat_stats.get('attack', 70),
            defense=combat_stats.get('defense', 70),
            speed=combat_stats.get('speed', 70),
            special=combat_stats.get('special', 50),
            cost=combat_stats.get('cost', 50),
            abilities=model.get('abilities', []),
            rarity=model.get('rarity', 'common')
        )
    
    def calculate_damage(self, attacker: Fighter, move: BattleMove, defender: Fighter) -> int:
        """Calculate damage for a move"""
        base_damage = 0
        
        if move == BattleMove.ANALYZE:
            # Intelligence-based attack
            base_damage = attacker.attack * 1.0
            self.log(f"{attacker.name} performs deep analysis!")
            
        elif move == BattleMove.CREATE:
            # Creativity-based attack (uses 80% attack + 20% special)
            base_damage = (attacker.attack * 0.8) + (attacker.special * 0.2)
            self.log(f"{attacker.name} generates creative solution!")
            
        elif move == BattleMove.SPEED_BLITZ:
            # Speed-based multi-hit
            hits = max(1, attacker.speed // 30)
            base_damage = (attacker.attack * 0.5) * hits
            self.log(f"{attacker.name} executes {hits}x speed blitz!")
            
        elif move == BattleMove.DEFEND:
            # Defensive move, small counter damage
            base_damage = attacker.defense * 0.3
            attacker.defense *= 1.5  # Temporary defense boost
            self.log(f"{attacker.name} takes defensive stance!")
            
        elif move == BattleMove.SPECIAL:
            # Special ability attack
            if attacker.abilities:
                ability = random.choice(attacker.abilities)
                base_damage = attacker.special * 1.2
                self.log(f"{attacker.name} uses {ability}!")
            else:
                base_damage = attacker.attack * 0.8
                self.log(f"{attacker.name} attempts special but has no abilities!")
                
        elif move == BattleMove.COST_DRAIN:
            # Cost-efficiency based drain attack
            base_damage = attacker.cost * 0.7
            heal_amount = int(base_damage * 0.3)
            attacker.heal(heal_amount)
            self.log(f"{attacker.name} drains resources! (+{heal_amount} HP)")
        
        # Apply rarity multiplier
        rarity_multipliers = {
            'common': 1.0,
            'uncommon': 1.1,
            'rare': 1.2,
            'epic': 1.3,
            'legendary': 1.5
        }
        multiplier = rarity_multipliers.get(attacker.rarity, 1.0)
        
        # Add some randomness (85% to 115%)
        randomness = random.uniform(0.85, 1.15)
        
        final_damage = int(base_damage * multiplier * randomness)
        
        # Critical hit chance (based on speed)
        if random.randint(1, 100) <= (attacker.speed // 10):
            final_damage = int(final_damage * 1.5)
            self.log("💥 CRITICAL HIT!")
        
        return final_damage
    
    def choose_move(self, fighter: Fighter, opponent: Fighter) -> BattleMove:
        """AI chooses the best move"""
        # Simple AI: choose move based on stats and situation
        
        # If low HP, more likely to defend or drain
        if fighter.hp_percentage < 30:
            if fighter.cost > fighter.attack:
                return BattleMove.COST_DRAIN
            else:
                return BattleMove.DEFEND
        
        # If has good special abilities and special stat
        if fighter.special > fighter.attack and fighter.abilities:
            if random.random() < 0.4:  # 40% chance
                return BattleMove.SPECIAL
        
        # If very fast, use speed blitz sometimes
        if fighter.speed > 85 and random.random() < 0.3:
            return BattleMove.SPEED_BLITZ
        
        # Otherwise, choose based on best stat
        best_stat = max(fighter.attack, fighter.speed, fighter.special, fighter.cost)
        
        if best_stat == fighter.attack:
            return random.choice([BattleMove.ANALYZE, BattleMove.CREATE])
        elif best_stat == fighter.speed:
            return BattleMove.SPEED_BLITZ
        elif best_stat == fighter.special:
            return BattleMove.SPECIAL
        else:
            return BattleMove.COST_DRAIN
    
    def battle_turn(self, fighter1: Fighter, fighter2: Fighter) -> bool:
        """Execute one turn of battle, return True if battle continues"""
        self.turn_count += 1
        self.log(f"\n=== Turn {self.turn_count} ===")
        self.log(f"{fighter1.name}: {fighter1.hp}/{fighter1.max_hp} HP")
        self.log(f"{fighter2.name}: {fighter2.hp}/{fighter2.max_hp} HP")
        
        # Determine turn order by speed
        if fighter1.speed >= fighter2.speed:
            first, second = fighter1, fighter2
        else:
            first, second = fighter2, fighter1
        
        # First fighter attacks
        if first.is_alive:
            move = self.choose_move(first, second)
            damage = self.calculate_damage(first, move, second)
            actual_damage = second.take_damage(damage)
            self.log(f"→ {second.name} takes {actual_damage} damage!")
        
        # Second fighter counters if still alive
        if second.is_alive:
            move = self.choose_move(second, first)
            damage = self.calculate_damage(second, move, first)
            actual_damage = first.take_damage(damage)
            self.log(f"→ {first.name} takes {actual_damage} damage!")
        
        # Check for winner
        if not fighter1.is_alive or not fighter2.is_alive:
            return False
        
        return True
    
    def battle(self, model1_id: str, model2_id: str, max_turns: int = 50) -> Dict:
        """Run a full battle between two models"""
        self.battle_log = []
        self.turn_count = 0
        
        # Create fighters
        fighter1 = self.create_fighter(model1_id)
        fighter2 = self.create_fighter(model2_id)
        
        if not fighter1 or not fighter2:
            return {
                'error': 'One or both models not found',
                'winner': None
            }
        
        self.log(f"⚔️ BATTLE START: {fighter1.name} vs {fighter2.name}!")
        self.log(f"Rarity: {fighter1.rarity} vs {fighter2.rarity}")
        
        # Battle loop
        while self.turn_count < max_turns:
            if not self.battle_turn(fighter1, fighter2):
                break
        
        # Determine winner
        winner = None
        if fighter1.is_alive and not fighter2.is_alive:
            winner = fighter1
            self.log(f"\n🏆 {fighter1.name} WINS!")
        elif fighter2.is_alive and not fighter1.is_alive:
            winner = fighter2
            self.log(f"\n🏆 {fighter2.name} WINS!")
        else:
            self.log(f"\n🤝 DRAW after {max_turns} turns!")
        
        return {
            'winner': winner.id if winner else None,
            'winner_name': winner.name if winner else "Draw",
            'turns': self.turn_count,
            'fighter1_hp': f"{fighter1.hp}/{fighter1.max_hp}",
            'fighter2_hp': f"{fighter2.hp}/{fighter2.max_hp}",
            'battle_log': self.battle_log
        }
    
    def tournament(self, model_ids: List[str]) -> Dict:
        """Run a tournament between multiple models"""
        if len(model_ids) < 2:
            return {'error': 'Need at least 2 models for tournament'}
        
        self.log("🏆 TOURNAMENT START!")
        results = {
            'participants': model_ids,
            'rounds': [],
            'champion': None
        }
        
        # Single elimination tournament
        current_round = model_ids.copy()
        round_num = 0
        
        while len(current_round) > 1:
            round_num += 1
            self.log(f"\n📯 ROUND {round_num}")
            next_round = []
            round_results = []
            
            # Pair up fighters
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    # Battle!
                    battle_result = self.battle(current_round[i], current_round[i + 1])
                    round_results.append(battle_result)
                    
                    if battle_result['winner']:
                        next_round.append(battle_result['winner'])
                    else:
                        # In case of draw, pick one randomly
                        next_round.append(random.choice([current_round[i], current_round[i + 1]]))
                else:
                    # Odd number, this one gets a bye
                    next_round.append(current_round[i])
                    self.log(f"{current_round[i]} gets a bye!")
            
            results['rounds'].append({
                'round': round_num,
                'battles': round_results
            })
            current_round = next_round
        
        if current_round:
            champion_id = current_round[0]
            champion = self.models.get(champion_id, {})
            results['champion'] = {
                'id': champion_id,
                'name': champion.get('name', champion_id)
            }
            self.log(f"\n🏆🏆🏆 TOURNAMENT CHAMPION: {champion.get('name', champion_id)}! 🏆🏆🏆")
        
        return results
    
    def log(self, message: str):
        """Add message to battle log"""
        self.battle_log.append(message)
        print(message)  # Also print to console

# Quick battle simulator
def quick_battle(model1: str, model2: str):
    """Quick battle between two models"""
    arena = BattleArena()
    result = arena.battle(model1, model2)
    return result

# Tournament runner
def run_tournament(model_ids: List[str]):
    """Run a tournament"""
    arena = BattleArena()
    result = arena.tournament(model_ids)
    return result

if __name__ == "__main__":
    # Example battle
    print("Starting example battle...")
    result = quick_battle("gpt-4-turbo", "claude-3-opus")
    print(f"\nBattle Result: {result['winner_name']} wins in {result['turns']} turns!")
