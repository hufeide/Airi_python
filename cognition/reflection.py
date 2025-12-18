
import threading

def reflect_async(memory, text):
    def worker():
        if len(text) > 10:
            memory.add(text)
    threading.Thread(target=worker, daemon=True).start()
