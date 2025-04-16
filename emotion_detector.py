from transformers import pipeline

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

def detect_emotion(text):
    result = emotion_classifier(text)[0]
    sorted_emotions = sorted(result, key=lambda x: x['score'], reverse=True)
    return sorted_emotions[0]['label'], sorted_emotions[0]['score']
