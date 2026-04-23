"""Basic usage example."""
from notebooklm import Notebook

nb = Notebook()
nb.add_text("The mitochondria is the powerhouse of the cell.", name="biology.txt")
nb.add_text("Python was created by Guido van Rossum in 1991.", name="python.txt")

answer = nb.chat("Who created Python and when?")
print(answer)
