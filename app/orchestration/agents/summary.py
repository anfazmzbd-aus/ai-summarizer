class SummaryAgent:

    def run(self, data):

        text = data["global_context"]["text"]

        return {
            "summary": text[:150]
        }