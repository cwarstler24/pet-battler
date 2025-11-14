import os
from typing import Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from dotenv import load_dotenv

load_dotenv()

class NarratorAgent:
	"""
	Creature Battle Narrator using local Hugging Face model for low-latency inference
	"""

	def __init__(self, model: str = "Qwen/Qwen2.5-0.5B-Instruct"):
		"""
		Initialize the local model for narration.
		Default model is Qwen2.5-0.5B-Instruct - an extremely fast, compact 0.5B parameter model
		optimized for instruction following and ultra-low latency.
		
		Other good options:
		- "Qwen/Qwen2.5-1.5B-Instruct" (1.5B, very fast, higher quality)
		- "HuggingFaceTB/SmolLM2-1.7B-Instruct" (1.7B, very fast)
		- "microsoft/Phi-3-mini-4k-instruct" (3.8B, slower but higher quality)
		"""
		self.model_name = model
		self.device = "cuda" if torch.cuda.is_available() else "cpu"
		
		print(f"Loading narrator model: {self.model_name} on {self.device}...")
		
		self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
		
		# Set padding token to avoid warnings
		if self.tokenizer.pad_token is None:
			self.tokenizer.pad_token = self.tokenizer.eos_token
		
		self.model = AutoModelForCausalLM.from_pretrained(
			self.model_name,
			torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
			device_map="auto" if self.device == "cuda" else None,
			trust_remote_code=True,
			low_cpu_mem_usage=True
		)
		
		if self.device == "cpu":
			self.model = self.model.to(self.device)
		
		self.model.eval()
		
		# Enable memory optimizations
		if hasattr(torch, 'set_num_threads'):
			torch.set_num_threads(4)  # Limit threads for faster inference
		
		# Try to compile model for speed (PyTorch 2.0+)
		try:
			if hasattr(torch, 'compile'):
				print("Compiling model for faster inference...")
				self.model = torch.compile(self.model, mode="reduce-overhead")
		except Exception as e:
			print(f"Could not compile model (this is okay): {e}")
		
		print(f"Model loaded successfully on {self.device}")

	def generate_narration(self, event: Dict[str, Any]) -> str:
		"""
		Generate a narration for a battle event.
		event: dict with keys like 'creature1', 'creature2', 'move1', 'move2', 'result', etc.
		"""
		prompt = self._format_prompt(event)
		
		try:
			# Simplified prompt for speed
			messages = [
				{"role": "user", "content": f"Narrate in 1 sentence: {prompt}"}
			]
			
			# Apply chat template
			formatted_prompt = self.tokenizer.apply_chat_template(
				messages,
				tokenize=False,
				add_generation_prompt=True
			)
			
			# Tokenize with minimal padding
			inputs = self.tokenizer(
				formatted_prompt,
				return_tensors="pt",
				truncation=True,
				max_length=128,  # Further reduced
				padding=False
			).to(self.device)
			
			# Ultra-fast greedy generation
			with torch.no_grad():
				outputs = self.model.generate(
					**inputs,
					max_new_tokens=25,  # Much shorter - forces brevity
					do_sample=False,    # Greedy is fastest (no sampling overhead)
					pad_token_id=self.tokenizer.pad_token_id,
					eos_token_id=self.tokenizer.eos_token_id,
					use_cache=True      # Faster generation
				)
			
			# Decode only the new tokens
			generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
			narration = self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
			
			# Simple cleanup
			if narration:
				# Remove incomplete sentences
				if narration[-1] not in '.!?':
					last_period = max(
						narration.rfind('.'), 
						narration.rfind('!'), 
						narration.rfind('?')
					)
					if last_period > 0:
						narration = narration[:last_period + 1]
				return narration
			
			return "The battle continues!"
			
		except Exception as e:
			print(f"Narration error: {e}")
			return "The battle rages on!"

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
