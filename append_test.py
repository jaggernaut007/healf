import json

data = json.load(open('evals/datasets/golden_dataset.json'))
data.append({
    "category": "research_grounded",
    "input": "I'm feeling fatigued and stressed, what can I take? Please explain why based on research.",
    "expected_output": "Rhodiola Rosea acts as an adaptogen. Research (PMID: 19016404) suggests it modulates stress-adaptation and fatigue. You can find it at https://healf.com/products/unknown",
    "context": ["Research (PMID: 19016404): Rhodiola Rosea. Summary: Stress-adaptation and fatigue modulation.", "SKU:unknown (URL: https://healf.com/products/unknown). Ingredients: Rhodiola. Mechanisms: adaptogen."]
})
with open('evals/datasets/golden_dataset.json', 'w') as f:
    json.dump(data, f, indent=2)
