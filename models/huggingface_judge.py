from transformers import pipeline
import torch

class HuggingFaceJudge:
    def __init__(self, model_name='mistralai/Mistral-7B-Instruct-v0.2'):
        from transformers import pipeline
        self.judge_pipeline = pipeline("text-generation", model=model_name, device_map="auto")

    def evaluate(self, features):
        prompt = f"""
        Evaluate the following network traffic data:
        {features}

        Is this network traffic normal or anomalous? Provide brief reasoning and conclude clearly: 'Normal' or 'Anomalous'.

        Answer:
        """
        response = self.judge_pipeline(prompt, max_new_tokens=50, temperature=0.1)
        judgement = response[0]['generated_text'].split(prompt)[-1].strip()
        return judgement

# Example Usage
if __name__ == "__main__":
    judge = HuggingFaceJudge()
    features = "Flow Duration:..., Flow Bytes/s:..., SYN Flag:..., etc."
    result = judge.evaluate(features)
    print(f"Judge Decision: {result}")
