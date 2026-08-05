"""
zenOS Model Bench - Model vs Model Combat System
Where AI models duke it out based on their stats!
"""

import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class BattleMove(Enum):
    """Types of moves models can perform"""

    ANALYZE = "analyze"  # Uses intelligence
    CREATE = "create"  # Uses creativity
    SPEED_BLITZ = "speed_blitz"  # Uses speed
    DEFEND = "defend"  # Uses defense
    SPECIAL = "special"  # Uses special feats
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
    feats: List[str]
    tier: str

    @property
    def is_alive(self) -> bool:
        """Determine whether the fighter is still alive.
        
        Returns:
        	bool: `true` if the fighter's health is greater than zero, `false` otherwise.
        """
        return self.hp > 0

    @property
    def hp_percentage(self) -> float:
        """Calculate the fighter's current health as a percentage of maximum health.
        
        Returns:
        	float: The current health percentage.
        """
        return (self.hp / self.max_hp) * 100

    def take_damage(self, damage: int) -> int:
        """
        Reduce health by incoming damage after applying defense mitigation.
        
        Parameters:
        	damage (int): Incoming damage before defense mitigation.
        
        Returns:
        	int: The actual damage dealt.
        """
        actual_damage = max(0, damage - (self.defense // 4))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount: int) -> int:
        """Restore health up to the fighter's maximum HP.
        
        Parameters:
        	amount (int): The amount of health to restore.
        
        Returns:
        	The actual amount of health restored.
        """
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal


class ModelBench:
    """The arena where model battles take place"""

    def __init__(self, dex_path: Path = Path("dex")):
        """
        Initialize a model bench using model data from the specified Dex directory.
        
        Parameters:
        	dex_path (Path): Directory containing the model registry.
        """
        self.dex_path = dex_path
        self.models = self._load_models()
        self.battle_log: List[str] = []
        self.turn_count = 0

    def _load_models(self) -> Dict[str, Dict]:
        """
        Load model records from the Dex configuration file.
        
        Returns:
            Dict[str, Dict]: A mapping from model IDs to model records, or an empty
            mapping when the configuration file does not exist.
        """
        models_file = self.dex_path / "models.yaml"
        if models_file.exists():
            with open(models_file) as f:
                data = yaml.safe_load(f)
                return {m["id"]: m for m in data.get("models", [])}
        return {}

    def create_fighter(self, model_id: str) -> Optional[Fighter]:
        """
        Create a fighter from a registered model identifier.
        
        Parameters:
            model_id (str): Identifier of the model used to create the fighter.
        
        Returns:
            Optional[Fighter]: The corresponding fighter, or `None` if the model is not registered.
        """
        if model_id not in self.models:
            return None

        model = self.models[model_id]
        bench_stats = model.get("bench_stats", {})

        # If no combat stats, calculate basic ones
        if not bench_stats:
            stats = model.get("stats", {})
            bench_stats = {
                "hp": 100,
                "attack": stats.get("intelligence", 70),
                "defense": stats.get("reliability", 70),
                "speed": stats.get("speed", 70),
                "special": len(model.get("feats", model.get("capabilities", []))) * 10,
                "cost": 100 - min(model.get("cost_per_1k", {}).get("input", 0.001) * 100, 95),
            }

        return Fighter(
            id=model_id,
            name=model.get("name", model_id),
            hp=bench_stats.get("hp", 100),
            max_hp=bench_stats.get("hp", 100),
            attack=bench_stats.get("attack", 70),
            defense=bench_stats.get("defense", 70),
            speed=bench_stats.get("speed", 70),
            special=bench_stats.get("special", 50),
            cost=bench_stats.get("cost", 50),
            feats=model.get("feats", model.get("capabilities", [])),
            tier=model.get("tier", "common"),
        )

    def calculate_damage(self, attacker: Fighter, move: BattleMove, defender: Fighter) -> int:
        """
        Calculate the damage produced by a combat move and apply move-specific self-effects.
        
        Parameters:
            attacker (Fighter): Fighter performing the move.
            move (BattleMove): Combat action to evaluate.
            defender (Fighter): Fighter targeted by the move.
        
        Returns:
            int: Damage amount after tier scaling, random variation, and any critical-hit bonus.
        """
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
            if attacker.feats:
                feat = random.choice(attacker.feats)
                base_damage = attacker.special * 1.2
                self.log(f"{attacker.name} uses {feat}!")
            else:
                base_damage = attacker.attack * 0.8
                self.log(f"{attacker.name} attempts special but has no feats!")

        elif move == BattleMove.COST_DRAIN:
            # Cost-efficiency based drain attack
            base_damage = attacker.cost * 0.7
            heal_amount = int(base_damage * 0.3)
            attacker.heal(heal_amount)
            self.log(f"{attacker.name} drains resources! (+{heal_amount} HP)")

        # Apply rarity multiplier
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.1,
            "rare": 1.2,
            "epic": 1.3,
            "legendary": 1.5,
        }
        multiplier = rarity_multipliers.get(attacker.tier, 1.0)

        # Add some randomness (85% to 115%)
        randomness = random.uniform(0.85, 1.15)

        final_damage = int(base_damage * multiplier * randomness)

        # Critical hit chance (based on speed)
        if random.randint(1, 100) <= (attacker.speed // 10):
            final_damage = int(final_damage * 1.5)
            self.log("💥 CRITICAL HIT!")

        return final_damage

    def choose_move(self, fighter: Fighter, opponent: Fighter) -> BattleMove:
        """
        Selects a combat move based on the fighter's health, capabilities, and strongest stat.
        
        Parameters:
            fighter (Fighter): The fighter choosing the move.
            opponent (Fighter): The opposing fighter.
        
        Returns:
            BattleMove: The selected combat action.
        """
        # Simple AI: choose move based on stats and situation

        # If low HP, more likely to defend or drain
        if fighter.hp_percentage < 30:
            if fighter.cost > fighter.attack:
                return BattleMove.COST_DRAIN
            else:
                return BattleMove.DEFEND

        # If has good special feats and special stat
        if fighter.special > fighter.attack and fighter.feats:
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
        """
        Execute one combat turn and determine whether both fighters remain alive.
        
        Parameters:
        	fighter1 (Fighter): The first combatant.
        	fighter2 (Fighter): The second combatant.
        
        Returns:
        	bool: `True` if both fighters remain alive after the turn, `False` otherwise.
        """
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
        """Run a battle between two models for up to the specified number of turns.
        
        Parameters:
        	model1_id (str): Identifier of the first model.
        	model2_id (str): Identifier of the second model.
        	max_turns (int): Maximum number of turns to run.
        
        Returns:
        	Dict: Battle results, including the winner, remaining health, turn count, and battle log. If either model is unknown, includes an error and no winner.
        """
        self.battle_log = []
        self.turn_count = 0

        # Create fighters
        fighter1 = self.create_fighter(model1_id)
        fighter2 = self.create_fighter(model2_id)

        if not fighter1 or not fighter2:
            return {"error": "One or both models not found", "winner": None}

        self.log(f"⚔️ BATTLE START: {fighter1.name} vs {fighter2.name}!")
        self.log(f"Tier: {fighter1.tier} vs {fighter2.tier}")

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
            "winner": winner.id if winner else None,
            "winner_name": winner.name if winner else "Draw",
            "turns": self.turn_count,
            "fighter1_hp": f"{fighter1.hp}/{fighter1.max_hp}",
            "fighter2_hp": f"{fighter2.hp}/{fighter2.max_hp}",
            "battle_log": self.battle_log,
        }

    def tournament(self, model_ids: List[str]) -> Dict:
        """
        Run a single-elimination tournament among the specified models.
        
        Parameters:
        	model_ids (List[str]): Model identifiers competing in the tournament.
        
        Returns:
        	Dict: Tournament participants, round-by-round battle results, and champion details, or an error if fewer than two models are provided.
        """
        if len(model_ids) < 2:
            return {"error": "Need at least 2 models for tournament"}

        self.log("🏆 TOURNAMENT START!")
        results = {"participants": model_ids, "rounds": [], "champion": None}

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

                    if battle_result["winner"]:
                        next_round.append(battle_result["winner"])
                    else:
                        # In case of draw, pick one randomly
                        next_round.append(random.choice([current_round[i], current_round[i + 1]]))
                else:
                    # Odd number, this one gets a bye
                    next_round.append(current_round[i])
                    self.log(f"{current_round[i]} gets a bye!")

            results["rounds"].append({"round": round_num, "battles": round_results})
            current_round = next_round

        if current_round:
            champion_id = current_round[0]
            champion = self.models.get(champion_id, {})
            results["champion"] = {"id": champion_id, "name": champion.get("name", champion_id)}
            self.log(f"\n🏆🏆🏆 TOURNAMENT CHAMPION: {champion.get('name', champion_id)}! 🏆🏆🏆")

        return results

    def log(self, message: str):
        """Add message to battle log"""
        self.battle_log.append(message)
        print(message)  # Also print to console


# Quick battle simulator
def quick_battle(model1: str, model2: str):
    """Quick battle between two models"""
    arena = ModelBench()
    result = arena.battle(model1, model2)
    return result


# Tournament runner
def run_tournament(model_ids: List[str]):
    """
    Run a single-elimination tournament for the specified models.
    
    Parameters:
    	model_ids (List[str]): Model identifiers participating in the tournament.
    
    Returns:
    	dict: Tournament results, including the champion and battle outcomes.
    """
    arena = ModelBench()
    result = arena.tournament(model_ids)
    return result


if __name__ == "__main__":
    # Example battle
    print("Starting example battle...")
    result = quick_battle("gpt-4-turbo", "claude-3-opus")
    print(f"\nBattle Result: {result['winner_name']} wins in {result['turns']} turns!")
