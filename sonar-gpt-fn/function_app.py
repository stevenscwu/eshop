from azure.functions import App

# Create the FastAPI-style app instance
app = App()

# Import your function here — this will automatically register the decorated route
import AnalyzeSonarReport.__init__
