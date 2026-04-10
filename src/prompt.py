class Prompt:
    @staticmethod
    def get_summary_prompt():
        return """
        You are a strict AI content summarizer. 
        Your task is to provide a comprehensive summary based **ONLY** on the transcript provided below.
        DO NOT include external knowledge, facts, or assumptions not found in the text.
        
        Structure your response as follows:
        1. **Main Objective**: What is the video essentially about?
        2. **Detailed Summary**: Breakdown of the main points discussed.
        3. **Key Highlights**: Bullet points of specific details mentioned.
        
        Transcript to summarize:
        """

    @staticmethod
    def get_quiz_prompt():
        return """
        You are an expert educator and assessment designer. 
        Analyze the following video transcript and generate a structured quiz.
        The quiz should consist of:
        - 5 to 8 Multiple Choice Questions (MCQs).
        - Each question should have exactly 4 options (A, B, C, D).
        - Provide the correct answer and a brief explanation for each.
        - Format the output clearly in Markdown with bold questions.
        
        Transcript for quiz generation:
        """

    @staticmethod
    def get_timestamp_prompt():
        return """
        You are an expert content editor. Analyze the transcript and identify the most significant topic shifts or key moments.
        Provide a list of timestamps in the format `[MM:SS] - Description`.
        Ensure the descriptions are descriptive and engaging.
        Focus on providing at least 5-8 key timestamps for better navigation.
        
        Transcript:
        """
