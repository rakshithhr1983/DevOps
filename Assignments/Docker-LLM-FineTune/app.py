import pandas as pd
from transformers import AutoModelForTokenClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# ============================================================
# Step 2: Prepare the Dataset
# ============================================================
data = {
    "text": [
        "Introduction to Computer Science",
        "Advanced Mathematics",
        "Data Structures and Algorithms",
        "Operating Systems",
        "Machine Learning"
    ],
    "labels": [
        ["Introduction to Computer Science"],
        ["Advanced Mathematics"],
        ["Data Structures and Algorithms"],
        ["Operating Systems"],
        ["Machine Learning"]
    ]
}

df = pd.DataFrame(data)

# Convert to Hugging Face Dataset
dataset = Dataset.from_pandas(df)

# ============================================================
# Step 3: Tokenization and Fine-tuning
# ============================================================
model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Tokenize the Dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Fine-tune the Model
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    num_train_epochs=3,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)
trainer.train()

# ============================================================
# Step 4: Create a FastAPI Application
# ============================================================
app = FastAPI()

class CourseRequest(BaseModel):
    text: str

@app.post("/extract-course-name/")
async def extract_course_name(request: CourseRequest):
    inputs = tokenizer(request.text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predictions = outputs.logits.argmax(dim=-1)
    extracted_names = [request.text]  # Replace with logic to extract names
    return {"extracted_course_names": extracted_names}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
