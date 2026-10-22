import os
import joblib
from django.core.management.base import BaseCommand
from django.conf import settings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from tracker.ai import SEED_DATA
from tracker.models import Transaction


class Command(BaseCommand):
    help = "Train and serialize the Naive Bayes NLP model and CountVectorizer to ml_models/ with joblib."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing Machine Learning training pipeline..."))

        # 1. Prepare base seed training data
        texts = [item[0] for item in SEED_DATA]
        labels = [item[1] for item in SEED_DATA]
        seed_count = len(texts)

        # 2. Augment with user transaction descriptions if available
        user_txs = Transaction.objects.filter(category__isnull=False).exclude(description__exact='').select_related('category')
        user_count = 0
        for tx in user_txs:
            clean = tx.description.strip().lower()
            if len(clean) >= 2:
                texts.append(clean)
                labels.append(tx.category.name)
                user_count += 1

        self.stdout.write(f"Aggregated {seed_count} seed merchant memos + {user_count} live transactions ({len(texts)} total samples).")

        # 3. Vectorize text with bi-grams
        vectorizer = CountVectorizer(stop_words='english', ngram_range=(1, 2))
        X = vectorizer.fit_transform(texts)
        vocab_size = len(vectorizer.vocabulary_)

        # 4. Fit Multinomial Naive Bayes classifier
        model = MultinomialNB(alpha=1.0)
        model.fit(X, labels)
        classes = list(model.classes_)

        # 5. Serialize models using joblib
        output_dir = settings.BASE_DIR / 'ml_models'
        os.makedirs(output_dir, exist_ok=True)

        model_path = output_dir / 'nlp_categorizer.joblib'
        vectorizer_path = output_dir / 'count_vectorizer.joblib'

        joblib.dump(model, model_path)
        joblib.dump(vectorizer, vectorizer_path)

        self.stdout.write(self.style.SUCCESS(
            f"[SUCCESS] ML Models serialized successfully!\n"
            f"  - Vocabulary Features: {vocab_size}\n"
            f"  - Classified Categories ({len(classes)}): {', '.join(classes)}\n"
            f"  - Model File: {model_path}\n"
            f"  - Vectorizer File: {vectorizer_path}"
        ))
