import datetime

class Log:
    def __init__(self, file):
        self.file = file
    
    def log(self, priority, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_message = f"[{timestamp}] [{priority.upper()}] {message}\n"
        
        with open(self.file, "a", encoding="utf-8") as f:
            match priority.lower():
                case "debug":
                    f.write(f"{formatted_message}")
                case "info":
                    f.write(f"{formatted_message}")
                case "warning" | "warn":
                    f.write(f"{formatted_message}")
                case "error":
                    f.write(f"{formatted_message}")
                case "critical":
                    f.write(f"{formatted_message}")
                case _:
                    f.write(f"{formatted_message}")
        
        print(formatted_message.strip())