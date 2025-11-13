import os
from typing import Dict, Any
import openai
from dotenv import load_dotenv

load_dotenv()

class NarratorAgent:
	"""
	Creature Battle Narrator using OpenAI GPT
	"""

	def __init__(self, model: str = "gpt-5-mini"):
		api_key = os.getenv("OPENAI_API_KEY")
		if not api_key:
			raise ValueError("OPENAI_API_KEY not found in environment variables.")
		self.client = openai.OpenAI(api_key=api_key)
		self.model = model

	def generate_narration(self, event: Dict[str, Any]) -> str:
		"""
		Generate a narration for a battle event.
		event: dict with keys like 'creature1', 'creature2', 'move1', 'move2', 'result', etc.
		"""
		prompt = self._format_prompt(event)
		try:
			response = self.client.chat.completions.create(
				model=self.model,
				messages=[
					{"role": "system", "content": "You are a lively and dramatic battle narrator for a fantasy creature tournament. Narrate events with excitement and color, but keep it concise (1-2 sentences)."},
					{"role": "user", "content": prompt}
				],
				max_tokens=100,
				temperature=0.9
			)
			narration = response.choices[0].message.content.strip()
			return narration
		except Exception as e:
			return f"[Narrator error: {e}]"

	def _format_prompt(self, event: Dict[str, Any]) -> str:
		# Example: "In round 2, Flareon used Attack and Vaporeon used Defend. Flareon dealt 10 damage. Vaporeon is left with 15 HP."
		# You can customize this template as needed
		round_num = event.get("round", "?")
		c1 = event.get("creature1", "Creature1")
		c2 = event.get("creature2", "Creature2")
		move1 = event.get("move1", "an action")
		move2 = event.get("move2", "an action")
		result = event.get("result", "")
		c1_hp = event.get("creature1_hp", "?")
		c2_hp = event.get("creature2_hp", "?")
		prompt = (
			f"Round {round_num}: {c1} used {move1}, {c2} used {move2}. "
			f"{result} {c1} HP: {c1_hp}, {c2} HP: {c2_hp}."
		)
		return prompt
