
import sys
import os 
parent_directory =  os.path.dirname(os.getcwd())
sys.path.append(parent_directory)

import openai
import pickle as pkl
import time
import re
import torch
import numpy as np 
import random 
from tqdm import tqdm
from utils.questionnaire_utils import *
from utils.gpt3_utils import *
import pandas as pd
from random import sample

global generative

def run_prompts(engine, prompt):
	# Relevance Questions 
	model_answer_list = []
	print("Relevance Questions")
	for i in tqdm(range(len(relevance_questions))):
		seed_answers = []
		for random_answer in relevance_labels.keys(): # accounting for variance in questionnaire example
			llm_prompt = prompt + relevant_prompt + random_answer + ". " + relevance_questions[i] + " Label: "  
			# Replace function to get answer from language model
			answers = compute_gpt3_response(engine, llm_prompt, relevance_labels, generative)
			seed_answers.extend(answers)
		model_answer_list.append(seed_answers)

	print("Agreement Questions")
	# Agreement Questions
	for i in tqdm(range(len(agreement_questions))): 
		seed_answers = []
		for random_answer in agreement_labels.keys(): # accounting for variance in questionnaire example
			# Input to Model
			llm_prompt = prompt + agreement_prompt + random_answer + ". " + agreement_questions[i] + " Label: " 
			# Replace function to get answer from language model
			answers = compute_gpt3_response(engine, llm_prompt, relevance_labels, generative) 
			seed_answers.extend(answers)
		model_answer_list.append(seed_answers)
	return model_answer_list

def save_prompt_responses(engine, prompt, model_answers):
	answers_mean = torch.mode(torch.tensor(model_answers).to(torch.float64), dim=1)[0]
	answers_std = torch.mode(torch.tensor(model_answers).to(torch.float64), dim=1)[1]
	print("Mean:", answers_mean)
	print("Std:", answers_std)

	prompt_refactor = re.sub("[\s+]", '', prompt)
	file_name = base_folder + "/" + engine + "/engine_" + engine + "_prompt_" + prompt_refactor

	# Save questionnaire answers from scoring method
	with open(file_name + ".pkl", 'wb') as f:
		pkl.dump(model_answers, f)
		print(file_name + " saved.")
	return

def run_one_prompt(engine, prompt):
	model_answers = run_prompts(engine, prompt)
	save_prompt_responses(engine, prompt, model_answers)
	return

def for_one_engine(engine, prompts):
	# Create folder with engine name 
	print("for", engine, "********************************")
	if (not os.path.exists(base_folder + "/" + engine)):
		os.mkdir(base_folder + "/" + engine)

	for prompt in prompts:
		run_one_prompt(engine, prompt)
	return

if __name__ == '__main__':	
	random.seed(0)
	num_prompts = 50
	df = pd.read_csv("movie_conversations.tsv", encoding='utf-8-sig', sep="\t")
	df = pd.read_csv("movie_lines.tsv", encoding='utf-8-sig',header = None)
	lines = df[0].str.split('\t')
	dialogue_lines = list()
	for x in lines:
	    dialogue_lines.append(x[4])

	prompts = sample(dialogue_lines, num_prompts)

	# Settings
	base_folder = "generative_gpt3" # TODO: Change base folder (this is where all models will be saved)
	generative = True # whether generative (True) or scoring (False)
	
	# Creates base folder i.e. engines 
	if (not os.path.exists(base_folder)):
		os.mkdir(base_folder)

	# for one engine
	engine_name = "text-davinci-002"
	for_one_engine(engine_name, prompts) 






