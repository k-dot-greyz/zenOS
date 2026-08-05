"""
Sample Text Processor Plugin for zenOS
This demonstrates how to create a Git-based VST plugin!
"""

import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from textblob import TextBlob


@dataclass
class ProcessingResult:
    """Result from text processing"""

    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TextProcessorPlugin:
    """Sample text processing plugin"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the text processor plugin with the supplied configuration.
        
        Parameters:
            config (Dict[str, Any]): Plugin configuration, including optional language,
                maximum input length, and sentiment analysis settings.
        """
        self.config = config
        self.language = config.get("language", "en")
        self.max_length = config.get("max_length", 1000)
        self.enable_sentiment = config.get("enable_sentiment", True)
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the text processor plugin.
        
        Returns:
        	bool: `True` if initialization succeeds, `False` if it fails.
        """
        try:
            # Initialize any required resources
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False

    async def process(self, input_data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process text according to the procedure specified in the context.
        
        Parameters:
        	input_data (Any): Text or text-containing data to process.
        	context (Dict[str, Any]): Procedure settings that determine the processing operation.
        
        Returns:
        	Dict[str, Any]: A result containing success status, processed data, and metadata, or an error message.
        """
        try:
            if not self.is_initialized:
                return {"success": False, "error": "Plugin not initialized"}

            # Extract text from input
            text = self._extract_text(input_data)
            if not text:
                return {"success": False, "error": "No text found in input"}

            # Check text length
            if len(text) > self.max_length:
                text = text[: self.max_length] + "..."

            # Get procedure from context
            procedure = context.get("procedure", {})
            procedure_id = procedure.get("id", "text.process")

            # Route to appropriate procedure
            if procedure_id == "text.process":
                result = await self._process_text(text, context)
            elif procedure_id == "text.summarize":
                result = await self._summarize_text(text, context)
            elif procedure_id == "text.sentiment":
                result = await self._analyze_sentiment(text, context)
            else:
                return {"success": False, "error": f"Unknown procedure: {procedure_id}"}

            return {
                "success": True,
                "data": result,
                "metadata": {
                    "procedure": procedure_id,
                    "text_length": len(text),
                    "language": self.language,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_text(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process text according to the requested operation.
        
        Parameters:
            text (str): Text to process.
            context (Dict[str, Any]): Operation name and operation-specific options.
        
        Returns:
            Dict[str, Any]: Operation results, or an error message for an unknown operation or processing failure.
        """
        try:
            # Get operation from context
            operation = context.get("operation", "analyze")

            if operation == "analyze":
                return await self._analyze_text(text)
            elif operation == "summarize":
                return await self._summarize_text(text, context)
            elif operation == "translate":
                return await self._translate_text(text, context)
            elif operation == "sentiment":
                return await self._analyze_sentiment(text, context)
            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for linguistic, language, sentiment, and readability metrics.
        
        Returns:
            Dict[str, Any]: Analysis results containing word count, sentence count,
            average word length, detected language, optional sentiment data, and
            readability score. Contains an ``error`` key if analysis fails.
        """
        try:
            blob = TextBlob(text)

            # Basic analysis
            word_count = len(blob.words)
            sentence_count = len(blob.sentences)
            avg_word_length = (
                sum(len(word) for word in blob.words) / word_count if word_count > 0 else 0
            )

            # Language detection
            detected_language = blob.detect_language()

            # Sentiment analysis
            sentiment = None
            if self.enable_sentiment:
                sentiment = {
                    "polarity": blob.sentiment.polarity,
                    "subjectivity": blob.sentiment.subjectivity,
                }

            return {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_word_length": round(avg_word_length, 2),
                "detected_language": detected_language,
                "sentiment": sentiment,
                "readability_score": self._calculate_readability(text),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _summarize_text(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an extractive summary of the text using the requested formatting style.
        
        Parameters:
            text (str): Text to summarize.
            context (Dict[str, Any]): Options including `max_sentences` and `style` (`bullet`, `paragraph`, or `outline`).
        
        Returns:
            Dict[str, Any]: Summary text with length, compression ratio, and sentence count, or an error message.
        """
        try:
            blob = TextBlob(text)
            sentences = blob.sentences

            # Get parameters
            max_sentences = context.get("max_sentences", 5)
            style = context.get("style", "bullet")

            # Simple extractive summarization (first N sentences)
            summary_sentences = sentences[:max_sentences]

            if style == "bullet":
                summary = "\n".join(f"• {str(sentence)}" for sentence in summary_sentences)
            elif style == "paragraph":
                summary = " ".join(str(sentence) for sentence in summary_sentences)
            elif style == "outline":
                summary = "\n".join(
                    f"{i+1}. {str(sentence)}" for i, sentence in enumerate(summary_sentences)
                )
            else:
                summary = " ".join(str(sentence) for sentence in summary_sentences)

            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": round(len(summary) / len(text), 2),
                "sentences_used": len(summary_sentences),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_sentiment(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the sentiment of text and optionally provide sentence-level details.
        
        Parameters:
            text (str): Text to analyze.
            context (Dict[str, Any]): Options controlling the analysis. Set ``detailed`` to
                ``True`` to include sentence-level sentiment and sentiment distribution.
        
        Returns:
            Dict[str, Any]: Sentiment polarity, subjectivity, and classification, with
                optional detailed results. Contains an ``error`` key if analysis fails.
        """
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment

            result = {
                "polarity": round(sentiment.polarity, 3),
                "subjectivity": round(sentiment.subjectivity, 3),
                "overall_sentiment": self._classify_sentiment(sentiment.polarity),
            }

            # Detailed analysis if requested
            if context.get("detailed", False):
                # Analyze by sentences
                sentence_sentiments = []
                for sentence in blob.sentences:
                    sent = sentence.sentiment
                    sentence_sentiments.append(
                        {
                            "text": str(sentence),
                            "polarity": round(sent.polarity, 3),
                            "subjectivity": round(sent.subjectivity, 3),
                        }
                    )

                result["sentence_analysis"] = sentence_sentiments
                result["sentiment_distribution"] = self._calculate_sentiment_distribution(
                    sentence_sentiments
                )

            return result

        except Exception as e:
            return {"error": str(e)}

    async def _translate_text(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate text to the language specified in the processing context when needed.
        
        Parameters:
            context (Dict[str, Any]): Processing context containing the target language under
                the ``language`` key; defaults to English when omitted.
        
        Returns:
            Dict[str, Any]: Translation details including the original text, translated text,
                source language, and target language. Includes a note when the text already
                uses the target language or an error message when translation fails.
        """
        try:
            target_language = context.get("language", "en")
            blob = TextBlob(text)

            # Detect source language
            source_language = blob.detect_language()

            # Translate if different from target
            if source_language != target_language:
                translated = blob.translate(to=target_language)
                return {
                    "original_text": text,
                    "translated_text": str(translated),
                    "source_language": source_language,
                    "target_language": target_language,
                }
            else:
                return {
                    "original_text": text,
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "note": "Text is already in target language",
                }

        except Exception as e:
            return {"error": str(e)}

    def _extract_text(self, input_data: Any) -> str:
        """
        Extract text from a string, mapping, list of strings, or other value.
        
        Parameters:
            input_data (Any): Value containing or representing the text.
        
        Returns:
            str: Extracted text, with list elements joined by spaces or other values converted to strings.
        """
        if isinstance(input_data, str):
            return input_data
        elif isinstance(input_data, dict):
            # Look for common text fields
            for field in ["text", "content", "message", "data"]:
                if field in input_data and isinstance(input_data[field], str):
                    return input_data[field]
        elif isinstance(input_data, list):
            # Join list of strings
            if all(isinstance(item, str) for item in input_data):
                return " ".join(input_data)

        return str(input_data)

    def _calculate_readability(self, text: str) -> float:
        """
        Calculate an approximate Flesch Reading Ease score for the text.
        
        Parameters:
            text (str): Text to evaluate.
        
        Returns:
            float: Readability score from 0.0 to 100.0, or 0.0 when the text cannot be evaluated.
        """
        try:
            blob = TextBlob(text)
            words = blob.words
            sentences = blob.sentences

            if len(words) == 0 or len(sentences) == 0:
                return 0.0

            # Simple Flesch Reading Ease approximation
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables = sum(self._count_syllables(word) for word in words) / len(words)

            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
            return round(max(0, min(100, score)), 1)

        except Exception:
            return 0.0

    def _count_syllables(self, word: str) -> int:
        """Estimate the number of syllables in a word.
        
        Returns:
        	int: An estimated syllable count of at least one.
        """
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # Handle silent 'e'
        if word.endswith("e") and syllable_count > 1:
            syllable_count -= 1

        return max(1, syllable_count)

    def _classify_sentiment(self, polarity: float) -> str:
        """
        Classify sentiment from a polarity score.
        
        Parameters:
        	polarity (float): Sentiment polarity score.
        
        Returns:
        	str: "positive" for scores above 0.1, "negative" for scores below -0.1, and "neutral" for all other scores.
        """
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"

    def _calculate_sentiment_distribution(self, sentence_sentiments: List[Dict]) -> Dict[str, int]:
        """
        Count sentence-level sentiment classifications.
        
        Parameters:
        	sentence_sentiments (List[Dict]): Sentence sentiment results containing polarity values.
        
        Returns:
        	Dict[str, int]: Counts of positive, negative, and neutral sentences.
        """
        distribution = {"positive": 0, "negative": 0, "neutral": 0}

        for sent in sentence_sentiments:
            sentiment_type = self._classify_sentiment(sent["polarity"])
            distribution[sentiment_type] += 1

        return distribution

    async def cleanup(self) -> bool:
        """
        Mark the plugin as no longer initialized.
        
        Returns:
            bool: `true` if cleanup succeeds, `false` if an exception occurs.
        """
        try:
            self.is_initialized = False
            return True
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return False


# Plugin instance factory
def create_plugin(config: Dict[str, Any]) -> TextProcessorPlugin:
    """Create a text processor plugin from the supplied configuration.
    
    Parameters:
    	config (Dict[str, Any]): Plugin configuration values.
    
    Returns:
    	TextProcessorPlugin: The configured text processor plugin.
    """
    return TextProcessorPlugin(config)
