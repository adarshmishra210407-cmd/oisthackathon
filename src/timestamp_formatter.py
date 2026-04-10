class TimestampFormatter:
    @staticmethod
    def format(raw_response):
        # Format the timestamp response cleanly
        return f"### Generated Timestamps\n\n{raw_response}\n\n*Note: Timestamps are based on transcript content.*"
