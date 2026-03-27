# Query model list
## Default input: models.json in the same folder as the script
python3 model_list.py

## Explicit path
python3 model_list.py /root/6/model_overview/models.json

# Specific model class
python3 model_list.py --openai
python3 model_list.py -p openai

# JSON array instead of plain lines
python3 model_list.py models.json --as-json

# Save to a file
python3 model_list.py models.json -o model_ids.txt


python3 model_list.py --qwen -o models_qwen.txt

# Model performance